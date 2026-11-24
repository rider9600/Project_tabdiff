# Compute log

Every run of the project, with how long it took: cluster jobs on Ada and steps run on the laptop.
Times are IST. Durations come from SLURM (`sacct` Elapsed), the scripts' own reports (`seconds` fields
in the JSON reports) or logs, never from memory. Failed and stopped runs are listed too.

## Ada jobs (1 x RTX 2080 Ti 11 GB, 10 CPUs, 28 GB per job)

| Job | Module | Node / GPU | Start | End | Hours | State | Runs done | Code | Notes |
|---|---|---|---|---|---|---|---|---|---|
| 99351 | env (tdr_env) | gnode043 / 2080 Ti | 24 Nov 12:16 | 24 Nov 12:26 | 0.15 | COMPLETED | env built (534 MB), 10 tests passed | 680d943 | no torch in the env yet (challenge 9) |
| 99363 | match (tdr_match) | gnode043 / 2080 Ti | 24 Nov 12:31 | 24 Nov 12:31 | 0.00 | FAILED 1:0 | 0 | 680d943 | GPU check: no torch in the project env (challenge 9) |
| 99364 | match (tdr_match), auto-resubmit of 99363 | gnode046 / 2080 Ti | 24 Nov 12:33 | 24 Nov 12:33 | 0.00 | FAILED 1:0 | 0 | 680d943 | same cause; resubmitted by the watcher as "infrastructure" |
| 99366 | env (tdr_env), rebuild with torch | gnode043 / 2080 Ti | 24 Nov 12:36 | 24 Nov 12:58 | 0.37 | COMPLETED | env 5.8 GB, torch 2.11.0+cu128, cuda ok, 15 tests passed | 751d9bd | Ada home now 95% full (1.5 GB free) |
| 99378 | match (tdr_match) | gnode043 / 2080 Ti | 24 Nov 12:58 | 24 Nov 18:03 | 5.08 | COMPLETED (time guard) | 17 of 20 chunks, 26,206 matched pieces | 751d9bd | 915 to 1,164 s per chunk of 50 taxis |
| 99794 | match (tdr_match), continuation | gnode043 / 2080 Ti | 24 Nov 18:07 | 24 Nov 18:47 | 0.66 | COMPLETED | chunks 18 to 20; all 20 done: 30,246 pieces, 98.6% of points matched | 751d9bd | 653 to 977 s per chunk |
| 99854 | train (tdr_train), tdrive_k300 | gnode043 / 2080 Ti | 24 Nov 18:52 | 24 Nov 18:53 | 0.01 | FAILED 1:0 | 0 | 7eb99da | DataLoader workers could not pickle TabDiff's lambda under Python 3.14 (challenge 10) |
| 99856 | train (tdr_train), tdrive_k300 | gnode043 / 2080 Ti | 24 Nov 18:55 | 24 Nov 18:55 | 0.01 | FAILED 1:0 | 0 | a860ba9 | CUDA out of memory with batch 4096 (challenge 11) |
| 99857 | train, batch 1024, 8,000 epochs | gnode043 / 2080 Ti | 24 Nov 18:58 | 24 Nov 19:21 | 0.39 | CANCELLED (by Claude) | 50+ epochs; loss 5.40 to 1.04 by epoch 50; about 25 s per epoch | fef0fd6 | 8,000 epochs would take ~55 h; restarted with 2,000 (decision 20) |
| 99878 | train, batch 1024, 2,000 epochs, checkpoint every 500 (EXP=e2000) | gnode043 / 2080 Ti | 24 Nov 19:21 | 25 Nov 01:21 | 6.00 | TIMEOUT (expected) | about 770 epochs; checkpoint 500 saved (loss 0.43 at 550); ~28 s per epoch | fef0fd6 | watcher crashed at the end (challenge 13); resubmitted by hand |
| 100223 | train, resume from model_500, checkpoint every 250 | | 25 Nov 01:25 (submitted) | | | running | | fef0fd6 | CHECK lowered to 250 to lose fewer epochs at each timeout |

## Laptop runs (8 cores, 16 GB RAM, no usable GPU for this work)

| Date, time | Step | Script | Duration | Input / output | Notes |
|---|---|---|---|---|---|
| 23 Nov (time not logged) | OSM road graph via Overpass API | scripts/prepare_osm.py (first version) | failed | 502 Bad Gateway | challenge 7 |
| 23 Nov, finished 19:55 | Download BBBike Beijing extract | curl | start not logged | 49.8 MB | |
| 23 Nov, finished 19:59 | Build road graph from the extract | scripts/prepare_osm.py | 201.1 s | 4.28M raw edges to 76,592 segments | osm_report.json |
| 24 Nov, about 11:20 | Profile raw T-Drive | scripts/profile_tdrive.py | 95.7 s | 17,662,984 rows | profile_report.json |
| 24 Nov, finished 11:26 | Clean T-Drive | scripts/clean_tdrive.py | 97.4 s | 17.66M to 11.77M points | tdrive_clean_report.json |
| 24 Nov, about 11:30 | Map-matching benchmark, default settings | scratch benchmark | 17 s map build + 1.1 s matching | 5 taxis, 197 points | 40% matched; 6 ms per point |
| 24 Nov, about 11:35 | Map-matching benchmark, sparse-data settings | scratch benchmark | 13 s map build + 12.4 s matching | 5 taxis, 164 points | 80% matched; 76 ms per point |
| 24 Nov, 11:30 to 11:42 | Map-matching smoke test | scripts/match_tdrive.py | 691.2 s (2 workers) | 4 taxis, 2,045 points | 95.5% matched; matched_smoke.report.json |
| 24 Nov, about 11:45 | One-taxi timing diagnostic | scratch diagnostic | stopped at 4 min by design | taxi 6598, 28 traversals | about 150 ms per point (shared CPU) |
| 24 Nov, 11:46 to 12:32 | Main map-matching run (1,000 taxis) | scripts/match_tdrive.py, 7 workers | 46 min, stopped | no chunk of 50 taxis finished | moved to Ada at the user's request (decision 18) |
| 24 Nov, about 11:55 | Transaction builder smoke test | scripts/build_transactions.py | not timed (seconds) | 4 taxis to 105 rows | |
| 24 Nov, about 12:45 | Evaluation suite smoke test | scripts/evaluate_synthetic.py | 548.0 s | smoke table, 2 seeds | slow query search; fixed afterwards |
| 24 Nov, from about 12:55 | TabDiff CPU smoke test with the graph-aware sampler | scripts/run_tabdiff.py | running | smoke table, 4 epochs | |

## Time summary (update after every run)

| Phase | Where | Wall-clock so far | Status |
|---|---|---|---|
| Data preparation (road graph, T-Drive profile and cleaning) | Laptop | about 6.6 min of compute (201 + 96 + 97 s) | done |
| Map-matching development (benchmarks, smoke test, diagnostic) | Laptop | about 17 min | done |
| Map-matching, main run | Laptop 46 min (stopped), then Ada | **Ada 5.74 h** (99378 5.08 h + 99794 0.66 h), 1,000 taxis | done |
| Ada environment setup | Ada | 0.52 h over 2 jobs (+ 2 failed starts of 0 s) | done |
| Transaction table | Laptop | 62 s (build_transactions.py) | done: 42,705 rows |
| TabDiff training | Ada | job 99854 from 18:55 | running |
| Sampling (default and graph-aware) | Ada | not started | |
| Evaluation | Laptop | smoke test 548 s | |

Before this project's Ada work, the teammate ran the TabDiff baseline (Adult, 8,000 epochs) on Google
Colab in 8 stages (experiments/stages/). Those runs are not logged here; their outputs are in
results/adult_8000/.

## Totals

| Part | Jobs / runs | Hours |
|---|---|---|
| Ada GPU jobs | 5 (2 complete, 2 failed at start, 1 running) | 0.52 (finished jobs) |
| Laptop runs | 13 | about 1.3 h of wall-clock |
