"""Export the TabDiff transaction table as fixed-length point sequences for DiffTraj (comparison, O6).

    .venv/Scripts/python scripts/difftraj_export.py --name tdrive_k300 --length 200

DiffTraj (Zhu et al., NeurIPS 2023) generates GPS trajectories of a fixed length plus 8 trip attributes.
To compare it with TabDiff on equal terms it is trained on exactly the same transactions (same taxis,
same split): each row of transactions.parquet is drawn as the polyline through its road segments
(projected metres, the same graph as the matcher), resampled to --length points evenly spaced along the
path, and normalised with the training mean and standard deviation.

Attributes (DiffTraj's "head", 8 values per trip), filled with what our table has:
  0 departure slot: 0 (time of day is not used, decision 6);  1 trip distance (m);  2 trip time: 0;
  3 number of segments;  4 mean segment length (m);  5 speed: 0;
  6, 7 start and end cell on a 16 x 16 grid over the window (0-255).
Columns 1, 3 and 4 are standardised with training statistics; DiffTraj's embeddings take 6 and 7.

Writes data_clean/difftraj/<name>/: traj_<split>.npy (n, length, 2), head_<split>.npy (n, 8),
norm.json (means, standard deviations, window box) and report.json.
"""

import argparse
import json
import time
from pathlib import Path

import numpy as np
import osmnx as ox
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
GRAPH_FILE = ROOT / "data_raw" / "osm" / "beijing_5th_ring_drive.graphml"
GRID = 16


def polyline(path_nodes, xy, geom):
    """Points along the segments of a path; uses the OSM segment geometry when there is one."""
    pts = []
    for u, v in zip(path_nodes[:-1], path_nodes[1:]):
        seg = list(geom[(u, v)].coords) if (u, v) in geom else [xy[u], xy[v]]
        pts.extend(seg if not pts else seg[1:])
    return np.asarray(pts, dtype=float)


def resample_along(pts: np.ndarray, n: int) -> np.ndarray:
    d = np.r_[0.0, np.cumsum(np.hypot(*np.diff(pts, axis=0).T))]
    s = np.linspace(0.0, d[-1], n)
    return np.c_[np.interp(s, d, pts[:, 0]), np.interp(s, d, pts[:, 1])]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--name", default="tdrive_k300")
    ap.add_argument("--length", type=int, default=200)   # DiffTraj default; the pre-trained UNet uses 200
    a = ap.parse_args()
    t0 = time.time()
    src = ROOT / "data_clean" / "tabdiff" / a.name
    out = ROOT / "data_clean" / "difftraj" / a.name
    out.mkdir(parents=True, exist_ok=True)

    edges = pd.read_csv(src / "edges.csv")
    tx = pd.read_parquet(src / "transactions.parquet")
    graph = ox.project_graph(ox.load_graphml(GRAPH_FILE))
    xy = {n: (d["x"], d["y"]) for n, d in graph.nodes(data=True)}
    geom = {(u, v): d["geometry"] for u, v, k, d in graph.edges(keys=True, data=True) if k == 0 and "geometry" in d}
    cols_uv = list(zip(edges["u"], edges["v"]))
    length_m = dict(zip(cols_uv, edges["length_m"]))

    def ordered_nodes(col_ids):
        """Edges of a transaction in travel order (each row is a simple path)."""
        es = [cols_uv[i] for i in col_ids]
        nxt = {u: v for u, v in es}
        start = ({u for u, _ in es} - {v for _, v in es}).pop()
        nodes = [start]
        while nodes[-1] in nxt:
            nodes.append(nxt[nodes[-1]])
        assert len(nodes) == len(es) + 1, "transaction is not a simple path"
        return nodes

    all_x = np.array([xy[n][0] for e in cols_uv for n in e])
    all_y = np.array([xy[n][1] for e in cols_uv for n in e])
    box = dict(xmin=float(all_x.min()), xmax=float(all_x.max()), ymin=float(all_y.min()), ymax=float(all_y.max()))

    def cell(x, y):
        i = min(int((x - box["xmin"]) / (box["xmax"] - box["xmin"] + 1e-9) * GRID), GRID - 1)
        j = min(int((y - box["ymin"]) / (box["ymax"] - box["ymin"] + 1e-9) * GRID), GRID - 1)
        return j * GRID + i

    data = {}
    for split in ("train", "val", "test"):
        part = tx[tx["split"] == split]
        trajs, heads = [], []
        for col_ids in part["edges"]:
            nodes = ordered_nodes(list(col_ids))
            pts = resample_along(polyline(nodes, xy, geom), a.length)
            dist = sum(length_m[(u, v)] for u, v in zip(nodes[:-1], nodes[1:]))
            k = len(nodes) - 1
            heads.append([0, dist, 0, k, dist / k, 0, cell(*pts[0]), cell(*pts[-1])])
            trajs.append(pts)
        data[split] = (np.asarray(trajs), np.asarray(heads, dtype=float))

    tr, hd = data["train"]
    mean, std = tr.reshape(-1, 2).mean(0), tr.reshape(-1, 2).std(0)
    hmean, hstd = hd.mean(0), hd.std(0)
    for c in (0, 2, 5):            # constant columns: leave as 0
        hmean[c], hstd[c] = 0.0, 1.0
    for c in (6, 7):               # categorical cells: not standardised
        hmean[c], hstd[c] = 0.0, 1.0
    for split, (t, h) in data.items():
        np.save(out / f"traj_{split}.npy", ((t - mean) / std).astype(np.float32))
        np.save(out / f"head_{split}.npy", ((h - hmean) / hstd).astype(np.float32))
    norm = {"length": a.length, "mean": mean.tolist(), "std": std.tolist(), "head_mean": hmean.tolist(),
            "head_std": hstd.tolist(), "box": box, "grid": GRID, "crs": str(graph.graph["crs"])}
    (out / "norm.json").write_text(json.dumps(norm, indent=2))
    rep = {"rows": {s: int(len(d[0])) for s, d in data.items()}, "length": a.length,
           "distance_m_median": float(np.median(hd[:, 1])), "seconds": round(time.time() - t0, 1)}
    (out / "report.json").write_text(json.dumps(rep, indent=2))
    print(json.dumps(rep))


if __name__ == "__main__":
    main()
