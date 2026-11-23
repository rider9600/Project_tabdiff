# Engineering

This project's own version of rules/03_ADA_HPC.md and rules/04_EXPERIMENTS_AND_CODE.md: layout, commands, job names, runbook.

**Status (23 November 2026): proposed, nothing built yet.** The layout below is a proposal to confirm
with the user before code is written (design changes are discussed first).

## Layout (proposed)

```
baseline_tabdiff/      the TabDiff code as inherited (kept unchanged; our sampler subclasses or wraps it)
src/roadtx/            our library: road graph, map-matching wrapper, transactions, encoding/decoding,
                       evaluation (validity, busy roads, patterns, popular paths, privacy), baselines,
                       graph-aware sampler
scripts/               prepare_data.py, make_modules.py, run_module.py (pushed)
                       ada_watch.py (laptop-side Ada watcher)
configs/               base.yaml, modules/<name>.yaml
tests/                 unittest: run all before every upload
analysis/              tables and figures from results
ada/                   module.sbatch, common.sh, upload.sh
results_ada/           copies of finished modules (local only)
```

## Ada

| Item | Value |
|---|---|
| Project folder | `~/tabdiff_roads/` with code/, data_clean/, out/<module>/, logs/ |
| Environment | `~/envs/tabdiff_roads` (built in the env job; until then common.sh falls back to `~/envs/qm`) |
| Job name prefix | `tdr` (e.g. `tdr_module`) |
| GPU | RTX 2080 Ti 11 GB (`--constraint=2080ti`); 6 h per job |
| Submit | `sbatch --export=ALL,PROJECT=tabdiff_roads,MODULE=<name> tabdiff_roads/code/ada/module.sbatch` |
| Upload | `PROJECT=tabdiff_roads bash ada/upload.sh <scratchpad>/stage` (after a commit) |
| Watcher | `PROJECT=tabdiff_roads python scripts/ada_watch.py --job <id> --sbatch "<args>" --expect-min <m> --log <scratchpad>/watch_log.jsonl` |

## Notes for TabDiff on this data

- Every segment column is binary categorical; TabDiff handles categorical columns with masked diffusion.
- The default TabDiff config is 8,000 epochs, batch 4096, validation every 2000 epochs
  (baseline_tabdiff/tabdiff/configs/tabdiff_configs.toml). We need validation every 500 epochs with our
  own quality metrics (decision 9).
- The inherited trainer has resume support (teammate's Colab work); check exact resume in the benchmark job.

## Runbook

As in rules/03_ADA_HPC.md, "Runbook". Project-specific steps are added here as they are built.
