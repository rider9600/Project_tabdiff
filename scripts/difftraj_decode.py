"""Turn DiffTraj point sequences into transaction rows (same columns as TabDiff's samples).

    .venv/Scripts/python scripts/difftraj_decode.py --points out.npy --out rows.csv [--every 10] [--workers 7]
    .venv/Scripts/python scripts/difftraj_decode.py --check val     # decoder accuracy on real trips

Each trajectory (projected metres, as written by run_difftraj.py) is thinned to every --every-th point
(the first and last are kept), map-matched with the same HMM matcher as the T-Drive pipeline
(leuvenmapmatching DistanceMatcher) on the road graph around the window, and turned into the set of
matched directed segments. A segment becomes a 1 in the row when it is one of the table's 300 columns,
exactly like the clipping of real transactions; segments outside the columns are dropped. A trajectory
that cannot be matched gives an empty row (it still counts in the evaluation).

--check <split> decodes the real exported trips of that split (data_clean/difftraj/<name>/traj_<split>.npy,
denormalised) and compares them with the true rows: this measures the decoder, not DiffTraj.
"""

import argparse
import json
import time
from multiprocessing import Pool
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
GRAPH_FILE = ROOT / "data_raw" / "osm" / "beijing_5th_ring_drive.graphml"
MARGIN_M = 500.0
# Generated points lie on a smooth curve with no GPS noise and close spacing, so the observation noise is
# smaller than for raw T-Drive (50 m there).
MATCHER_KW = dict(max_dist=500, max_dist_init=60, obs_noise=15, obs_noise_ne=40, dist_noise=30,
                  max_lattice_width=10, min_prob_norm=1e-30, non_emitting_length_factor=0.95,
                  non_emitting_states=True, only_edges=True)

_MAP = None


def _init(box):
    global _MAP
    import osmnx as ox
    from leuvenmapmatching.map.inmem import InMemMap

    graph = ox.project_graph(ox.load_graphml(GRAPH_FILE))
    keep = {n for n, d in graph.nodes(data=True)
            if box["xmin"] - MARGIN_M <= d["x"] <= box["xmax"] + MARGIN_M
            and box["ymin"] - MARGIN_M <= d["y"] <= box["ymax"] + MARGIN_M}
    _MAP = InMemMap("window", use_latlon=False, use_rtree=True, index_edges=True)
    for n in keep:
        d = graph.nodes[n]
        _MAP.add_node(n, (d["y"], d["x"]))
    for u, v in graph.edges():
        if u in keep and v in keep:
            _MAP.add_edge(u, v)


def _match(args):
    from leuvenmapmatching.matcher.distance import DistanceMatcher

    xy, every = args
    idx = sorted(set(range(0, len(xy), every)) | {len(xy) - 1})
    pts = [(float(xy[i, 1]), float(xy[i, 0])) for i in idx]
    try:
        m = DistanceMatcher(_MAP, **MATCHER_KW)
        _, last = m.match(pts)
        nodes = m.path_pred_onlynodes
    except Exception:
        return [], 0.0
    nodes = [n for k, n in enumerate(nodes) if k == 0 or n != nodes[k - 1]]
    return list(zip(nodes[:-1], nodes[1:])), (last + 1) / len(pts)


def decode(points: np.ndarray, edges: pd.DataFrame, box: dict, every: int, workers: int):
    col = {(u, v): c for c, u, v in zip(edges["column"], edges["u"], edges["v"])}
    with Pool(workers, initializer=_init, initargs=(box,)) as pool:
        res = pool.map(_match, [(p, every) for p in points], chunksize=20)
    rows = np.zeros((len(points), len(edges)), dtype=np.int8)
    pos = {c: i for i, c in enumerate(edges["column"])}
    for r, (segs, _) in enumerate(res):
        for s in segs:
            if s in col:
                rows[r, pos[col[s]]] = 1
    df = pd.DataFrame(rows, columns=list(edges["column"]))
    return df, float(np.mean([f for _, f in res]))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--name", default="tdrive_k300")
    ap.add_argument("--points", default="")
    ap.add_argument("--out", default="")
    ap.add_argument("--check", default="", help="decode the real trips of this split and compare")
    ap.add_argument("--limit", type=int, default=0, help="only the first N trajectories")
    ap.add_argument("--every", type=int, default=10)
    ap.add_argument("--workers", type=int, default=7)
    a = ap.parse_args()
    t0 = time.time()
    tab = ROOT / "data_clean" / "tabdiff" / a.name
    dt = ROOT / "data_clean" / "difftraj" / a.name
    edges = pd.read_csv(tab / "edges.csv")
    norm = json.loads((dt / "norm.json").read_text())
    if a.check:
        pts = np.load(dt / f"traj_{a.check}.npy") * np.array(norm["std"]) + np.array(norm["mean"])
    else:
        pts = np.load(a.points)
    if a.limit:
        pts = pts[: a.limit]
    df, matched = decode(pts, edges, norm["box"], a.every, a.workers)
    rep = {"trajectories": len(df), "points_matched_share": round(matched, 4),
           "empty_rows": round(float((df.sum(axis=1) == 0).mean()), 4),
           "segments_per_row": round(float(df.sum(axis=1).mean()), 3), "seconds": round(time.time() - t0, 1)}
    if a.check:
        truth = pd.read_csv(tab / f"{a.check}.csv")[list(edges["column"])].astype(str).eq("1").to_numpy()[: len(df)]
        got = df.to_numpy().astype(bool)
        inter, union = (truth & got).sum(1), (truth | got).sum(1)
        rep.update(exact_rows=round(float((truth == got).all(1).mean()), 4),
                   jaccard_mean=round(float(np.mean(inter / np.maximum(union, 1))), 4),
                   true_segments_per_row=round(float(truth.sum(1).mean()), 3))
    if a.out:
        df.to_csv(a.out, index=False)
    print(json.dumps(rep))


if __name__ == "__main__":
    main()
