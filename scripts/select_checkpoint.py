"""Score every sampled table against the real validation split and pick a checkpoint per sampler.

    python scripts/select_checkpoint.py --samples results_ada/sample/e2000 --name tdrive_k300

Tables are named <sampler>_e<epoch>_s<seed>.csv (ada/sample.sbatch). Scores are cheap levels only:
trip validity, row length, busy roads and frequent patterns (popular paths and privacy are left to the
final evaluation). The checkpoint score is the mean of four [0, 1] terms, higher is better:
  1 - |mean segments per row (syn) - (real)| / (real), valid share of non-empty rows,
  busy-road Spearman, and the recall of real multi-segment frequent itemsets.
Writes <samples>/selection.json and prints a table.
"""

import argparse
import json
import re
import sys
import time
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from roadtx import evaluate as ev  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--samples", required=True)
    ap.add_argument("--name", default="tdrive_k300")
    a = ap.parse_args()
    t0 = time.time()
    d = ROOT / "data_clean" / "tabdiff" / a.name
    edges = pd.read_csv(d / "edges.csv")
    train, val = pd.read_csv(d / "train.csv"), pd.read_csv(d / "val.csv")
    cols = ev.segment_columns(val)
    min_count_train = ev.min_support_count(train)
    min_count = max(int(round(min_count_train * len(val) / len(train))), 2)
    real_len = float(ev.to_bool(val[cols]).sum(axis=1).mean())
    rows = []
    for p in sorted(Path(a.samples).glob("*_e*_s*.csv*")):
        m = re.match(r"([^_]+)_e(\d+)_s(\d+)\.csv", p.name)
        syn = pd.read_csv(p)
        b = ev.to_bool(syn[cols])
        trips = ev.trip_validity(syn, edges)
        nonempty = 1 - trips["share_empty"]
        busy = ev.busy_roads(val, syn)
        pat = ev.pattern_fidelity(val, syn, edges, min_count)
        syn_len = float(b.sum(axis=1).mean())
        terms = [max(0.0, 1 - abs(syn_len - real_len) / real_len),
                 trips["share_valid"] / nonempty if nonempty else 0.0,
                 max(0.0, busy["spearman_segment_use"]),
                 pat["recall_real_itemsets"]]
        rows.append({"sampler": m.group(1), "epoch": int(m.group(2)), "seed": int(m.group(3)),
                     "segments_per_row": round(syn_len, 3), "share_empty": trips["share_empty"],
                     "share_valid": trips["share_valid"], "valid_of_nonempty": round(terms[1], 4),
                     "share_gap": trips["share_gap"], "share_branch": trips["share_branch"],
                     "spearman": busy["spearman_segment_use"], "top50": busy["top50_overlap"],
                     "itemset_recall": pat["recall_real_itemsets"], "itemset_jaccard": pat["jaccard_multi_itemsets"],
                     "contiguity_maximal_syn": pat["contiguity_maximal_syn"],
                     "score": round(sum(terms) / len(terms), 4)})
        print(f"scored {p.name}", flush=True)
    df = pd.DataFrame(rows).sort_values(["sampler", "epoch"])
    best = {s: int(g.loc[g["score"].idxmax(), "epoch"]) for s, g in df.groupby("sampler")}
    out = {"real_val_segments_per_row": round(real_len, 3), "min_count_val": min_count,
           "best_epoch": best, "rows": df.to_dict("records"), "seconds": round(time.time() - t0, 1)}
    Path(a.samples, "selection.json").write_text(json.dumps(out, indent=2))
    print(df.to_string(index=False))
    print("best epoch per sampler:", best, f"({out['seconds']} s)")


if __name__ == "__main__":
    main()
