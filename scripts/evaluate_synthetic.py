"""Evaluate synthetic transaction tables against the real data, with reference points and baselines.

    .venv/Scripts/python scripts/evaluate_synthetic.py --name tdrive_k300 [--synthetic name=path.csv ...]

Always evaluates:
- real_test: held-out real transactions (other taxis) as if they were synthetic; the best achievable score;
- independent and markov baselines, fitted on the real training split, 3 seeds each.
Then every --synthetic table (e.g. TabDiff with the default and the graph-aware sampler).

minF (decision 8): third quartile of single-segment support counts in the real training split;
lowered to the median if that gives fewer than 100 multi-segment itemsets on real data.
Writes data_clean/tabdiff/<name>/evaluation.json and prints a summary table.
"""

import argparse
import json
import sys
import time
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from roadtx import baselines  # noqa: E402
from roadtx import evaluate as ev  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--name", default="tdrive_k300")
    ap.add_argument("--synthetic", nargs="*", default=[], help="label=path.csv")
    ap.add_argument("--seeds", type=int, default=3)
    ap.add_argument("--queries", type=int, default=10)
    a = ap.parse_args()

    start = time.time()
    d = ROOT / "data_clean" / "tabdiff" / a.name
    train, test = pd.read_csv(d / "train.csv", dtype=str), pd.read_csv(d / "test.csv", dtype=str)
    edges = pd.read_csv(d / "edges.csv")
    trans = pd.read_parquet(d / "transactions.parquet")
    train_tx = [list(t) for t in trans.loc[trans["split"] == "train", "edges"]]

    min_count, rule = ev.min_support_count(train, 0.75), "q3"
    if sum(len(k) > 1 for k in ev.frequent_itemsets(train, min_count)) < 100:
        min_count, rule = ev.min_support_count(train, 0.5), "median"
    queries = ev.choose_queries(train, edges, a.queries)
    n = len(test)

    results = {"name": a.name, "min_count_train": min_count, "min_count_rule": rule,
               "rows_train": len(train), "rows_test": len(test), "queries": [list(map(int, q)) for q in queries],
               "methods": {}}
    results["methods"]["real_test"] = [ev.evaluate_all(train, test, test, edges, min_count, queries)]
    for label, fn in (("independent", lambda s: baselines.independent(train, edges, n, s)),
                      ("markov", lambda s: baselines.markov(train_tx, edges, n, s))):
        results["methods"][label] = [ev.evaluate_all(train, test, fn(s), edges, min_count, queries)
                                     for s in range(a.seeds)]
    for item in a.synthetic:
        label, path = item.split("=", 1)
        syn = pd.read_csv(path, dtype=str)
        results["methods"][label] = [ev.evaluate_all(train, test, syn, edges, min_count, queries)]

    results["seconds"] = round(time.time() - start, 1)
    (d / "evaluation.json").write_text(json.dumps(results, indent=2, default=float))

    keys = [("trips", "share_valid"), ("busy_roads", "top25_overlap"), ("busy_roads", "spearman_segment_use"),
            ("patterns", "jaccard_multi_itemsets"), ("patterns", "contiguity_maximal_syn"),
            ("popular_paths", "kendall_tau_mean"), ("popular_paths", "kendall_tau_mean_no_minf"),
            ("trips", "segments_per_row_mean"), ("trips", "share_gap"), ("privacy", "exact_copy_share")]
    table = {label: {f"{a_}.{b_}": round(float(pd.Series([r[a_][b_] for r in runs]).mean()), 4) for a_, b_ in keys}
             for label, runs in results["methods"].items()}
    print(f"minF = {min_count} ({rule}); {len(queries)} queries; {results['seconds']} s")
    print(pd.DataFrame(table).T.to_string())


if __name__ == "__main__":
    main()
