"""Build the transaction table for TabDiff from map-matched routes.

    .venv/Scripts/python scripts/build_transactions.py --matched data_clean/matched_traversals.parquet \
        --name tdrive_k300 --k 300 --window-km 4

Steps:
1. Split every matched route into transactions with the backtracking rule (Rathan, Reddy & Mondal 2022).
2. Area: a square window of --window-km around the densest 500 m cell of edge use (or --center).
3. Columns: the --k most-used directed road segments inside the window (decision 6).
4. Clip each transaction to maximal runs of kept segments, so no gaps are created; keep runs with at
   least --min-edges segments. Each run is one row.
5. Split rows by taxi into train / validation / test (70 / 10 / 20), so a taxi never appears in two splits.
6. Write the TabDiff table: one "0"/"1" column per segment plus the target column length_km.

Output folder data_clean/tabdiff/<name>/: train.csv, val.csv, test.csv, info.json, edges.csv,
transactions.parquet (edge lists per row, with taxi and split), report.json.
Data stays local / on the user's Ada account (T-Drive licence: no redistribution).
"""

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

import numpy as np
import osmnx as ox
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from roadtx.transactions import chain, clip_runs, split_backtracking  # noqa: E402

GRAPH_FILE = ROOT / "data_raw" / "osm" / "beijing_5th_ring_drive.graphml"
CELL_M = 500.0


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--matched", default=str(ROOT / "data_clean" / "matched_traversals.parquet"))
    ap.add_argument("--name", default="tdrive_k300")
    ap.add_argument("--k", type=int, default=300, help="number of road-segment columns")
    ap.add_argument("--window-km", type=float, default=4.0, help="side of the square area")
    ap.add_argument("--center", default="", help="lon,lat of the area centre (default: densest cell)")
    ap.add_argument("--min-edges", type=int, default=2)
    ap.add_argument("--seed", type=int, default=0)
    a = ap.parse_args()

    graph = ox.project_graph(ox.load_graphml(GRAPH_FILE))
    crs = graph.graph["crs"]
    xy = {n: (d["x"], d["y"]) for n, d in graph.nodes(data=True)}

    matched = pd.read_parquet(a.matched)
    utts, owners = [], []
    for taxi, nodes in zip(matched["taxi"], matched["nodes"]):
        for utt in split_backtracking(list(nodes)):
            if len(utt) >= a.min_edges:
                utts.append(utt)
                owners.append(int(taxi))
    use = Counter(e for utt in utts for e in set(utt))

    def mid(e):
        (x1, y1), (x2, y2) = xy[e[0]], xy[e[1]]
        return (x1 + x2) / 2, (y1 + y2) / 2

    if a.center:
        from pyproj import Transformer
        lon, lat = map(float, a.center.split(","))
        cx, cy = Transformer.from_crs("EPSG:4326", crs, always_xy=True).transform(lon, lat)
    else:
        cells = Counter()
        for e, c in use.items():
            x, y = mid(e)
            cells[(int(x // CELL_M), int(y // CELL_M))] += c
        (i, j), _ = cells.most_common(1)[0]
        cx, cy = (i + 0.5) * CELL_M, (j + 0.5) * CELL_M
    half = a.window_km * 500.0

    def inside(e):
        x, y = mid(e)
        return abs(x - cx) <= half and abs(y - cy) <= half

    in_window = [e for e in use if inside(e)]
    columns = sorted(in_window, key=lambda e: -use[e])[: a.k]
    keep = set(columns)

    rows, row_taxi = [], []
    for utt, taxi in zip(utts, owners):
        for run in clip_runs(utt, keep, a.min_edges):
            rows.append(run)
            row_taxi.append(taxi)
    assert all(chain(r) is not None for r in rows), "a clipped transaction is not a simple path"

    taxis = np.array(sorted(set(row_taxi)))
    rng = np.random.default_rng(a.seed)
    rng.shuffle(taxis)
    n = len(taxis)
    split_of = {t: "train" for t in taxis[: int(0.7 * n)]}
    split_of.update({t: "val" for t in taxis[int(0.7 * n): int(0.8 * n)]})
    split_of.update({t: "test" for t in taxis[int(0.8 * n):]})

    col_index = {e: i for i, e in enumerate(columns)}
    names = [f"e{i:03d}" for i in range(len(columns))]
    length = {(u, v): float(d["length"]) for u, v, k, d in graph.edges(keys=True, data=True) if k == 0}
    table = np.zeros((len(rows), len(columns)), dtype=np.int8)
    for r, run in enumerate(rows):
        for e in run:
            table[r, col_index[e]] = 1
    df = pd.DataFrame(table.astype(str), columns=names)
    df["length_km"] = [round(sum(length[e] for e in run) / 1000.0, 4) for run in rows]
    split = np.array([split_of[t] for t in row_taxi])

    out = ROOT / "data_clean" / "tabdiff" / a.name
    out.mkdir(parents=True, exist_ok=True)
    for s in ("train", "val", "test"):
        df[split == s].to_csv(out / f"{s}.csv", index=False)
    info = {
        "name": a.name, "task_type": "regression", "header": "infer",
        "column_names": names + ["length_km"], "num_col_idx": [], "cat_col_idx": list(range(len(names))),
        "target_col_idx": [len(names)], "file_type": "csv",
        "data_path": f"data/{a.name}/train.csv", "val_path": f"data/{a.name}/val.csv",
        "test_path": f"data/{a.name}/test.csv",
        "column_info": {**{c: "str" for c in names}, "length_km": "float"},
        "train_num": int((split == "train").sum()), "test_num": int((split == "test").sum()),
    }
    (out / "info.json").write_text(json.dumps(info, indent=2))
    edges = pd.DataFrame({"column": names, "u": [e[0] for e in columns], "v": [e[1] for e in columns],
                          "length_m": [length[e] for e in columns], "use_count": [use[e] for e in columns]})
    edges.to_csv(out / "edges.csv", index=False)
    pd.DataFrame({"taxi": row_taxi, "split": split, "edges": [[col_index[e] for e in r] for r in rows]}) \
        .to_parquet(out / "transactions.parquet", index=False)

    sizes = [len(r) for r in rows]
    report = {
        "matched_pieces": len(matched), "taxis": int(matched["taxi"].nunique()),
        "utts_before_area": len(utts), "distinct_edges_used": len(use),
        "area_centre_projected_m": [round(cx), round(cy)], "window_km": a.window_km,
        "edges_in_window": len(in_window), "columns": len(columns),
        "min_use_of_a_column": int(use[columns[-1]]) if columns else 0,
        "rows": len(rows), "rows_train_val_test": [int((split == s).sum()) for s in ("train", "val", "test")],
        "edges_per_row_median": float(np.median(sizes)) if sizes else 0,
        "edges_per_row_quantiles_10_90": [float(np.quantile(sizes, q)) for q in (0.1, 0.9)] if sizes else [],
        "length_km_median": float(df["length_km"].median()) if len(df) else 0,
    }
    (out / "report.json").write_text(json.dumps(report, indent=2))
    # MD5s that the Ada training job checks before it runs (rules/03, data check).
    import hashlib
    files = ["train.csv", "val.csv", "test.csv", "info.json", "edges.csv", "transactions.parquet"]
    (out / "md5.json").write_text(json.dumps({f: hashlib.md5((out / f).read_bytes()).hexdigest() for f in files},
                                             indent=2))
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
