# Compute log

One row per cluster job or Kaggle notebook.

| Job | Module | Node / GPU | Start | End | Hours | State | Runs done | Code | Notes |
|---|---|---|---|---|---|---|---|---|---|
| 99351 | env (tdr_env) | gnode043 / 2080 Ti | 24 Nov 12:16 | 24 Nov 12:26 | 0.15 | COMPLETED | env built (534 MB), 10 tests passed | 680d943 | no torch in the env yet (challenge 9) |
| 99363 | match (tdr_match) | gnode043 / 2080 Ti | 24 Nov 12:31 | 24 Nov 12:31 | 0.00 | FAILED 1:0 | 0 | 680d943 | GPU check: no torch in the project env (challenge 9) |
| 99364 | match (tdr_match), auto-resubmit of 99363 | gnode046 / 2080 Ti | 24 Nov 12:33 | 24 Nov 12:33 | 0.00 | FAILED 1:0 | 0 | 680d943 | same cause; resubmitted by the watcher as "infrastructure" |
| 99366 | env (tdr_env), rebuild with torch | gnode043 / 2080 Ti | 24 Nov 12:36 | 24 Nov 12:58 | 0.37 | COMPLETED | env 5.8 GB, torch 2.11.0+cu128, cuda ok, 15 tests passed | 751d9bd | Ada home now 95% full (1.5 GB free) |
| 99378 | match (tdr_match) | | 24 Nov 12:59 (submitted) | | | running | | 751d9bd | 1,000 taxis, chunks of 50, guard 5.5 h |

Before this project's Ada work, the teammate ran the TabDiff baseline (Adult, 8,000 epochs) on Google
Colab in 8 stages (experiments/stages/). Those runs are not logged here; their outputs are in
results/adult_8000/.

## Totals

| Part | Jobs | GPU h |
|---|---|---|
| Ada | 5 | 0.52 |
