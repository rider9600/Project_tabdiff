"""Mean and 95% confidence interval over seeds for every method and metric.

    .venv/Scripts/python scripts/summarise_results.py results_ada/final_all/evaluation.json [more.json ...] --out table.md

Labels "<method>_s<seed>" are grouped by method; the interval is the t-interval over seeds (3 seeds:
t = 4.30). Methods evaluated once (real_test) get no interval. Several evaluation files (same dataset,
same queries) can be merged. Writes a Markdown table and prints it.
"""

import argparse
import json
import re

import numpy as np
import pandas as pd
from scipy import stats

METRICS = [("trips", "share_valid", "valid"), ("trips", "share_gap", "gaps"),
           ("trips", "segments_per_row_mean", "seg/row"), ("busy_roads", "spearman_segment_use", "Spearman"),
           ("busy_roads", "top25_overlap", "top-25"), ("patterns", "jaccard_multi_itemsets", "itemset J"),
           ("patterns", "contiguity_maximal_syn", "contig."),
           ("popular_paths", "kendall_tau_mean_no_minf", "tau"), ("privacy", "exact_copy_share", "copies")]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="+")
    ap.add_argument("--out", default="")
    a = ap.parse_args()
    runs = {}
    for f in a.files:
        for label, rs in json.load(open(f))["methods"].items():
            m = re.sub(r"_s\d+$", "", label)
            if m in runs and m in ("real_test", "independent", "markov") and f != a.files[0]:
                continue
            runs.setdefault(m, []).extend(rs)
    rows = {}
    for m, rs in runs.items():
        row = {}
        for sec, key, name in METRICS:
            v = np.array([r[sec][key] for r in rs], dtype=float)
            v = v[~np.isnan(v)]
            if len(v) == 0:
                row[name] = "-"
            elif len(v) == 1:
                row[name] = f"{v[0]:.3f}"
            else:
                h = stats.t.ppf(0.975, len(v) - 1) * v.std(ddof=1) / np.sqrt(len(v))
                row[name] = f"{v.mean():.3f} ± {h:.3f}"
        rows[m] = row
    df = pd.DataFrame(rows).T
    cols = list(df.columns)
    md = "\n".join(["| method | " + " | ".join(cols) + " |", "|---" * (len(cols) + 1) + "|"]
                   + [f"| {m} | " + " | ".join(str(r[c]) for c in cols) + " |" for m, r in df.iterrows()])
    if a.out:
        open(a.out, "w", encoding="utf-8").write(md + "\n")
    print(md)


if __name__ == "__main__":
    main()
