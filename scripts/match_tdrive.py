"""Map-match cleaned T-Drive points onto the Beijing road graph with leuvenmapmatching.

    .venv/Scripts/python scripts/match_tdrive.py --taxis 200 --workers 8 --out data_clean/matched_pilot.parquet
    .venv/Scripts/python scripts/match_tdrive.py --taxis 1000 --workers 7 --chunk-dir data_clean/match_chunks

With --chunk-dir, taxis are processed in chunks of CHUNK taxis, each saved as its own parquet file.
A rerun skips chunks that already exist, so an interrupted run continues where it stopped.

On Ada (rules/03): --time-limit-h with --session-start makes the run stop starting new chunks when
elapsed + 1.2 x the slowest chunk so far would pass the limit. It then exits with code 0 and prints
"TIME GUARD"; resubmitting the job continues with the remaining chunks. When every chunk is done, it
writes the combined parquet, its report, and module_report.json in the chunk folder.

Per taxi:
1. Project points to metres (the graph's UTM zone) and drop points within MIN_MOVE_M of the previous
   kept point (taxi standing still; the time gap that remains still marks the stop).
2. Split into traversals at gaps longer than GAP_S (Reddy et al.'s break threshold t_w).
3. Match each traversal with an HMM matcher (leuvenmapmatching DistanceMatcher, settings tuned on a
   sample for ~3-minute sampling). If matching breaks part-way, restart from the break point, so a
   traversal can give several matched pieces.
4. Keep the matched node sequence of each piece, with consecutive duplicate nodes removed.

Output parquet, one row per matched piece: taxi, piece_id, t_start, t_end, n_points, nodes (list of
OSM node ids along the route, in travel order). A JSON report with counts and timing sits next to it.
Data stays local / on the user's Ada account (T-Drive licence: no redistribution).
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
POINTS_FILE = ROOT / "data_clean" / "tdrive_points.parquet"

MIN_MOVE_M = 30.0      # drop a point closer than this to the previous kept point
GAP_S = 900            # a gap longer than 15 minutes ends a traversal
MIN_POINTS = 3         # shorter traversals or pieces are not matched / kept
CHUNK = 50             # taxis per saved chunk (resume unit)
MATCHER_KW = dict(max_dist=2500, max_dist_init=150, obs_noise=50, obs_noise_ne=200, dist_noise=200,
                  max_lattice_width=10, min_prob_norm=1e-30, non_emitting_length_factor=0.95,
                  non_emitting_states=True, only_edges=True)

_MAP = None
_CRS = None


def _init_worker(graph_file=GRAPH_FILE) -> None:
    """Build the in-memory map once per worker process."""
    global _MAP, _CRS
    import osmnx as ox
    from leuvenmapmatching.map.inmem import InMemMap

    graph = ox.project_graph(ox.load_graphml(graph_file))
    _CRS = graph.graph["crs"]
    _MAP = InMemMap("beijing", use_latlon=False, use_rtree=True, index_edges=True)
    for n, d in graph.nodes(data=True):
        _MAP.add_node(n, (d["y"], d["x"]))
    for u, v in graph.edges():
        _MAP.add_edge(u, v)


def _traversals(df: pd.DataFrame):
    """Yield (times, xy) arrays per traversal for one taxi, after the stationary filter and gap split."""
    from pyproj import Transformer

    tr = Transformer.from_crs("EPSG:4326", _CRS, always_xy=True)
    x, y = tr.transform(df["lon"].values, df["lat"].values)
    t = df["t"].values
    keep = [0]
    for i in range(1, len(x)):
        j = keep[-1]
        if np.hypot(x[i] - x[j], y[i] - y[j]) >= MIN_MOVE_M:
            keep.append(i)
    keep = np.array(keep)
    x, y, t = x[keep], y[keep], t[keep]
    gaps = np.r_[0, (np.diff(t).astype("timedelta64[s]").astype(np.int64) > GAP_S).cumsum()]
    for g in np.unique(gaps):
        idx = np.where(gaps == g)[0]
        if len(idx) >= MIN_POINTS:
            yield t[idx], np.column_stack([y[idx], x[idx]])


def _match_taxi(args):
    taxi, df = args
    from leuvenmapmatching.matcher.distance import DistanceMatcher

    rows, stats = [], {"traversals": 0, "points": 0, "points_matched": 0, "breaks": 0}
    for times, yx in _traversals(df):
        stats["traversals"] += 1
        stats["points"] += len(yx)
        start = 0
        while len(yx) - start >= MIN_POINTS:
            matcher = DistanceMatcher(_MAP, **MATCHER_KW)
            try:
                _, last = matcher.match([tuple(p) for p in yx[start:]])
            except Exception:  # a failed traversal piece is skipped, never fatal
                last = -1
            n_ok = last + 1
            if n_ok >= MIN_POINTS:
                nodes = matcher.path_pred_onlynodes
                nodes = [n for k, n in enumerate(nodes) if k == 0 or n != nodes[k - 1]]
                if len(nodes) >= 2:
                    rows.append({"taxi": int(taxi), "t_start": times[start], "t_end": times[start + n_ok - 1],
                                 "n_points": int(n_ok), "nodes": [int(n) for n in nodes]})
                    stats["points_matched"] += n_ok
            if start + max(n_ok, 1) < len(yx):
                stats["breaks"] += 1
            start += max(n_ok, 1)
    return rows, stats


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--taxis", type=int, default=0, help="match only this many randomly chosen taxis (pilot)")
    ap.add_argument("--taxi-fraction", type=float, default=0.0, help="match this random fraction of taxis")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--out", default=str(ROOT / "data_clean" / "matched_traversals.parquet"))
    ap.add_argument("--chunk-dir", default="", help="save and resume per chunk of taxis")
    ap.add_argument("--graph", default=str(GRAPH_FILE))
    ap.add_argument("--points", default=str(POINTS_FILE))
    ap.add_argument("--time-limit-h", type=float, default=0.0, help="stop starting chunks near this limit")
    ap.add_argument("--session-start", type=float, default=0.0, help="job start (epoch s); default now")
    a = ap.parse_args()

    start = time.time()
    session_start = a.session_start or start
    slowest_chunk = 1800.0      # assumed until a chunk has been timed (30 min)
    stopped_by_guard = False
    pts = pd.read_parquet(a.points)
    all_taxis = np.sort(pts["taxi"].unique())
    rng = np.random.default_rng(a.seed)
    if a.taxis:
        chosen = rng.choice(all_taxis, a.taxis, replace=False)
    elif a.taxi_fraction:
        chosen = rng.choice(all_taxis, int(round(a.taxi_fraction * len(all_taxis))), replace=False)
    else:
        chosen = all_taxis
    pts = pts[pts["taxi"].isin(set(chosen.tolist()))]
    jobs = [(taxi, g) for taxi, g in pts.groupby("taxi", sort=True)]

    totals = {"traversals": 0, "points": 0, "points_matched": 0, "breaks": 0}
    chunk_dir = Path(a.chunk_dir) if a.chunk_dir else None
    if chunk_dir:
        chunk_dir.mkdir(parents=True, exist_ok=True)
    chunks = [jobs[i:i + CHUNK] for i in range(0, len(jobs), CHUNK)]
    frames = []
    with Pool(a.workers, initializer=_init_worker, initargs=(a.graph,)) as pool:
        for c, chunk in enumerate(chunks):
            path = chunk_dir / f"chunk_{c:04d}.parquet" if chunk_dir else None
            if path is not None and path.exists():
                frames.append(pd.read_parquet(path))
                stats = json.loads(path.with_suffix(".json").read_text())
                for key in totals:
                    totals[key] += stats[key]
                print(f"chunk {c + 1}/{len(chunks)} already done, skipped", flush=True)
                continue
            if a.time_limit_h and time.time() - session_start + 1.2 * slowest_chunk > a.time_limit_h * 3600:
                print(f"TIME GUARD: stopping before chunk {c + 1}/{len(chunks)} "
                      f"({(time.time() - session_start) / 3600:.2f} h elapsed); resubmit to continue", flush=True)
                stopped_by_guard = True
                break
            chunk_start = time.time()
            rows, ctot = [], {key: 0 for key in totals}
            for r, s in pool.imap_unordered(_match_taxi, chunk, chunksize=1):
                rows.extend(r)
                for key in ctot:
                    ctot[key] += s[key]
            frame = pd.DataFrame(rows)
            if path is not None:
                frame.to_parquet(path, index=False)
                path.with_suffix(".json").write_text(json.dumps(ctot))
            frames.append(frame)
            for key in totals:
                totals[key] += ctot[key]
            took = time.time() - chunk_start
            slowest_chunk = took if c == 0 or slowest_chunk == 1800.0 else max(slowest_chunk, took)
            done = sum(len(f) for f in frames)
            print(f"chunk {c + 1}/{len(chunks)} done in {took:.0f} s: {done} pieces so far, "
                  f"{time.time() - start:.0f} s", flush=True)

    if stopped_by_guard:
        return

    out = pd.concat(frames, ignore_index=True).sort_values(["taxi", "t_start"]).reset_index(drop=True)
    out.insert(1, "piece_id", np.arange(len(out)))
    out_path = Path(a.out)
    out.to_parquet(out_path, index=False)
    secs = time.time() - start
    report = {
        "taxis_matched": len(jobs), "taxis_available": int(len(all_taxis)), "seed": a.seed,
        **totals, "pieces": len(out),
        "point_match_rate": round(totals["points_matched"] / max(totals["points"], 1), 4),
        "median_nodes_per_piece": float(out["nodes"].map(len).median()) if len(out) else 0,
        "seconds": round(secs, 1), "workers": a.workers,
        "seconds_per_taxi_per_worker": round(secs * a.workers / max(len(jobs), 1), 2),
        "settings": {"MIN_MOVE_M": MIN_MOVE_M, "GAP_S": GAP_S, "MIN_POINTS": MIN_POINTS, **MATCHER_KW},
    }
    out_path.with_suffix(".report.json").write_text(json.dumps(report, indent=2, default=str))
    if chunk_dir:
        (chunk_dir / "module_report.json").write_text(json.dumps(
            {"module": "match", "chunks": len(chunks), "all_done": True, **report}, indent=2, default=str))
    print(json.dumps(report, indent=2, default=str))


if __name__ == "__main__":
    main()
