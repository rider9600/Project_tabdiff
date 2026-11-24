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
    if os.name == "nt":
        # Windows can't send TabDiff's lambda transforms to DataLoader worker processes (Linux forks,
        # so Ada is unaffected). On the laptop only, load data in the main process.
        import torch.utils.data as tud

        _init = tud.DataLoader.__init__

        def _init_no_workers(self, *args, **kwargs):
            kwargs["num_workers"] = 0
            kwargs.pop("persistent_workers", None)
            kwargs.pop("prefetch_factor", None)
            _init(self, *args, **kwargs)

        tud.DataLoader.__init__ = _init_no_workers
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
