# Resume here: live state (updated 24 November 2026, 22:45 IST)

A new session reads CLAUDE.md, this file and the end of WORKLOG.md, then carries on with the queue below.

## 1. Where it stands

| Item | State |
|---|---|
| Running now | **Ada training job 99878** (tdr_train, tdrive_k300, EXP=e2000, 2,000 epochs, checkpoint every 500, batch 1,024). Started 24 Nov 19:22 IST; ~28 s per epoch; epoch 350 at 22:10 (loss 0.48). Expect TIMEOUT at 6 h (~01:20), watcher resubmits; total ~15.5 h, done ~11:00 on 25 Nov |
| Exact resubmit command | `sbatch --export=ALL,PROJECT=tabdiff_roads,NAME=tdrive_k300,STEPS=2000,CHECK=500,EXP=e2000 tabdiff_roads/code/ada/train.sbatch` (resumes from newest model_<epoch>.pt) |
| Watcher | scripts/ada_watch.py on 99878 (laptop background) + Monitor on scratchpad watch_log.jsonl. **Restart both in every new session** |
| Code on Ada | fef0fd6 (latest pushed: see git log) |
| Ada disk | 24 GB of 25 GB used (1.4 GB free). Each checkpoint (model + ema) ~100 MB; 4 expected |
| Laptop copies | results_ada/match/ (matched_traversals.parquet + report) |
| Compute used | see compute_log.md (Ada ~7.7 h so far) |

## 2. Finished

| Part | Result | Where |
|---|---|---|
| Data | T-Drive cleaned (11.77M points); road graph 34,135 nodes / 76,592 segments | DATA.md |
| Map-matching | Ada 99378 + 99794 (5.74 h): 1,000 taxis, 30,246 pieces, 98.6% of points matched | DATA.md, results_ada/match |
| Table tdrive_k300 | 42,705 rows (train 29,378 / val 4,566 / test 8,761, by taxi), 300 columns + length_km | data_clean/tabdiff/tdrive_k300 (laptop and Ada) |
| Code | transactions, evaluate, baselines, graph_sampler (+ tests, 19 pass); runner run_tabdiff.py | src/roadtx, scripts, tests |

## 3. Left, in this order

| Order | Step | How |
|---|---|---|
| 1 | Finish training (99878 + resubmits) | watcher |
| 2 | Sampling job on Ada for each checkpoint (500..2000) on the **validation** split: default sampler and graph-aware (strength 0.5), seed 0 | write ada/sample.sbatch: `run_tabdiff.py [--graph-edges ...] --skip-tabdiff-eval --seed S --sample-batch-size 2000 --samples-out ... -- --dataname tdrive_k300 --mode test --ckpt_path <model_E.pt> --no_wandb --exp_name e2000` |
| 3 | Pick best checkpoint by our metrics on val (validity + pattern overlap) | scripts/evaluate_synthetic.py |
| 4 | Final: best checkpoint, 3 seeds x {default, graph-aware}, evaluate vs real_test, independent, markov | evaluate_synthetic.py --synthetic label=path ... |
| 5 | Report + slides; remove placeholder results (needs the user's OK) | docs/ |

## 4. How to restart

1. Check `squeue`/`sacct` on Ada and `git status`.
2. Start a watcher for any running job (command above) and arm a Monitor on its log.
3. Continue with section 3.
