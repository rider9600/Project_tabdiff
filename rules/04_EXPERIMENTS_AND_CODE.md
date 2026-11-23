# 4. Experiments and code

## Layout

```
src/<package>/     library code (models, data, training, evaluation)
scripts/           entry points: prepare_data.py, make_modules.py, run_module.py
configs/           base.yaml, tuned.yaml, modules/<name>.yaml (generated)
ada/               sbatch files, common.sh, upload.sh
tests/             unittest; run all before every upload
analysis/          scripts that turn results into tables and figures
results_ada/       copies of every finished module (git-ignored if large)
```

## Experiments are modules

- Each experiment is split into **modules**: lists of runs that fit one 6 h job. `make_modules.py`
  generates them from the plan, using measured speeds, and refuses any module over 5 h.
- **Each run is defined by its config and seed.** Its output folder holds `summary.json` and
  `metrics_round.csv` (or per-epoch metrics), plus the saved model.
- **Resume is exact:** checkpoint often (model, optimizer, scheduler, scaler, step, every random state),
  keep the last two checkpoints, and delete them when the run finishes. A test must show that a stopped
  and resumed run gives the same result as an unbroken one.
- **Finished runs are skipped**, so resubmitting a module continues it.
- **Time guard:** no run starts unless elapsed + 1.2 x predicted <= 5.5 h. Refit the speed model from
  real run times (benchmarks often run up to 30% fast).
- **Save every trained model.** Copy each module's outputs to the laptop as soon as it ends.

## Order of work for a study

1. Data: download (ask first), clean with a script, and write DATA.md with counts and checksums.
   Measure on all rows or a random sample, never on the head of a file.
2. Engine: copy proven code from an earlier project at a tagged commit. Adapt it, then write tests.
3. Hypotheses: register them in HYPOTHESES.md before the main runs.
4. Pilot: a short run of the main settings to confirm everything learns.
5. Tuning on validation only, with the grid in the plan. If the best value sits at the edge of the
   grid, run the next value beyond it.
6. Main experiments with 3 or more seeds, chosen on validation and reported on test.
7. Ablations, extra settings and analyses.

## Checking

- Look at real outputs after every job: predictions, score curves, best rounds. Look for collapse
  (one class predicted for everything), NaNs, a best score at the last round (training may need to run
  longer), and differences between seeds.
- Never measure on training data. Select models on validation and report on test.
- Odd results (a baseline beating the method, a collapse) are recorded in challenges.md and reported.
  Never quietly drop them.
- Keep the unit tests passing (`python -m unittest`). Add a test for each bug you fix.
