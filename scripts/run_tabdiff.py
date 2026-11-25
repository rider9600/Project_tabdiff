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
    ap.add_argument("--remask-mode", choices=["graph", "random"], default="graph",
                    help="random: control arm, same number of re-masked columns per row at random places")
    ap.add_argument("--skip-tabdiff-eval", action="store_true",
                    help="training: skip TabDiff's in-loop sample evaluation (checkpoints are still saved); "
                         "test: only sample and save samples.csv, without TabDiff's metrics and plots")
    ap.add_argument("--seed", type=int, default=None, help="seed torch, numpy and random before TabDiff starts")
    ap.add_argument("--samples-out", default="", help="test mode: copy the generated samples.csv here")
    ap.add_argument("--train-batch-size", type=int, default=None, help="override [train.main] batch_size")
    ap.add_argument("--sample-batch-size", type=int, default=None, help="override [sample] batch_size")
    a = ap.parse_args(own)
    train_mode = "test" not in passthrough[passthrough.index("--mode") + 1:passthrough.index("--mode") + 2] \
        if "--mode" in passthrough else True

    sys.path.insert(0, str(TABDIFF))
    sys.path.insert(0, str(ROOT / "src"))
    if True:
        # TabDiff's lambda transforms can't be sent to DataLoader worker processes unless they are
        # forked: Windows spawns, and Python 3.14 on Linux (Ada) defaults to forkserver. The table is
        # small (8 batches per epoch), so load data in the main process everywhere.
        import torch.utils.data as tud

        _init = tud.DataLoader.__init__

        def _init_no_workers(self, *args, **kwargs):
            kwargs["num_workers"] = 0
            kwargs.pop("persistent_workers", None)
            kwargs.pop("prefetch_factor", None)
            _init(self, *args, **kwargs)

        tud.DataLoader.__init__ = _init_no_workers
    if a.seed is not None:
        import random

        import numpy as np
        import torch

        random.seed(a.seed)
        np.random.seed(a.seed)
        torch.manual_seed(a.seed)
        torch.cuda.manual_seed_all(a.seed)
    if a.train_batch_size or a.sample_batch_size:
        # Override TabDiff's config values in memory (the 4096 default does not fit 300 columns on 11 GB).
        import src as tabdiff_src
        import tabdiff.main as tabdiff_main_module

        _load = tabdiff_src.load_config

        def load_config(path):
            cfg = _load(path)
            if a.train_batch_size:
                cfg["train"]["main"]["batch_size"] = a.train_batch_size
            if a.sample_batch_size:
                cfg["sample"]["batch_size"] = a.sample_batch_size
            return cfg

        tabdiff_src.load_config = load_config
        tabdiff_main_module.src.load_config = load_config
    saved = {}
    if a.skip_tabdiff_eval:
        import tabdiff.trainer as tt

        def evaluate_generation(self, save_metric_details=False, plot_density=False, ema=False):
            if train_mode:          # checkpoints were already saved by run_loop; skip sampling entirely
                return {}, {}, None
            self.diffusion.eval()
            n = self.num_samples_to_generate or self.metrics.real_data_size
            syn_df = self.sample_synthetic(n, ema=ema)
            save_path = os.path.join(self.result_save_path, str(self.curr_epoch), "ema" if ema else "")
            os.makedirs(save_path, exist_ok=True)
            path = os.path.join(save_path, "samples.csv")
            syn_df.to_csv(path, index=False)
            saved["path"] = path
            print(f"Samples are saved at {path}", flush=True)
            return {}, {}, None

        tt.Trainer.evaluate_generation = evaluate_generation
    stats = None
    if a.graph_edges:
        import pandas as pd
        import tabdiff.models.unified_ctime_diffusion as ucd
        from roadtx import graph_sampler

        edges = pd.read_csv(Path(a.graph_edges).resolve())
        graph_sampler.install(ucd.UnifiedCtimeDiffusion, edges, a.graph_strength, a.remask_mode)
        stats = graph_sampler.STATS
        print(f"re-masking sampler installed ({a.remask_mode}): {len(edges)} segments, strength {a.graph_strength}", flush=True)

    os.chdir(TABDIFF)
    sys.argv = ["main.py"] + passthrough
    try:
        runpy.run_path(str(TABDIFF / "main.py"), run_name="__main__")
    finally:
        if a.samples_out and saved.get("path"):
            import shutil

            out = Path(a.samples_out)
            if not out.is_absolute():
                out = ROOT / out
            out.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(saved["path"], out)
            print(f"samples copied to {out}", flush=True)
        if stats and stats["calls"]:
            print(f"graph-aware sampler: {stats['calls']} re-masking calls, mean flagged share "
                  f"{stats['flagged_share_sum'] / stats['calls']:.4f}", flush=True)


if __name__ == "__main__":
    main()
