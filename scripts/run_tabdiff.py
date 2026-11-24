"""Run TabDiff's main.py, optionally with the graph-aware stochastic sampler installed.

    python scripts/run_tabdiff.py [--graph-edges data_clean/tabdiff/<name>/edges.csv --graph-strength 0.5] \
        -- --dataname <name> --mode train --no_wandb ...

Everything after "--" is passed to baseline_tabdiff/main.py unchanged. With --graph-edges, TabDiff's
sampler is patched in memory (src/roadtx/graph_sampler.py) before main.py starts; baseline_tabdiff/ is
not edited. After the run, the share of re-masking calls with flagged segments is printed.
"""

import argparse
import os
import runpy
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TABDIFF = ROOT / "baseline_tabdiff"


def main() -> None:
    argv = sys.argv[1:]
    passthrough = argv[argv.index("--") + 1:] if "--" in argv else []
    own = argv[:argv.index("--")] if "--" in argv else argv
    ap = argparse.ArgumentParser()
    ap.add_argument("--graph-edges", default="")
    ap.add_argument("--graph-strength", type=float, default=0.5)
    a = ap.parse_args(own)

    sys.path.insert(0, str(TABDIFF))
    sys.path.insert(0, str(ROOT / "src"))
    stats = None
    if a.graph_edges:
        import pandas as pd
        import tabdiff.models.unified_ctime_diffusion as ucd
        from roadtx import graph_sampler

        edges = pd.read_csv(Path(a.graph_edges).resolve())
        graph_sampler.install(ucd.UnifiedCtimeDiffusion, edges, a.graph_strength)
        stats = graph_sampler.STATS
        print(f"graph-aware sampler installed: {len(edges)} segments, strength {a.graph_strength}", flush=True)

    os.chdir(TABDIFF)
    sys.argv = ["main.py"] + passthrough
    try:
        runpy.run_path(str(TABDIFF / "main.py"), run_name="__main__")
    finally:
        if stats and stats["calls"]:
            print(f"graph-aware sampler: {stats['calls']} re-masking calls, mean flagged share "
                  f"{stats['flagged_share_sum'] / stats['calls']:.4f}", flush=True)


if __name__ == "__main__":
    main()
