# Work log while the user is away

Everything Claude does on its own is listed here, newest last, so it can be reported when the user returns. Details live in the other record files.

| Time (IST) | Event | Action and reason | Details |
|---|---|---|---|
| 23 November 2026, 13:07 | Framework received | Placed rules/, records, ada/ and the watcher, all local only (user instruction) | DECISIONS.md 3 |
| 23 November 2026, 13:08 | .gitignore edit by the user | Reverted the uncommitted `framework` line; the local exclude covers it | DECISIONS.md 3 |
| 23 November 2026, 13:10 | Ada scripts configured | Project `tabdiff_roads`, prefix `tdr`; upload.sh copies the local ada/ | DECISIONS.md 3 and 4 (to confirm) |
| 23 November 2026, 13:12 | Records filled in | Decisions 1 to 12 from today's discussion; challenges 1 to 5 | DECISIONS.md, challenges.md |
| 23 November 2026, 13:40 | Publishing rule narrowed by the user | Only CLAUDE.md, DECISIONS.md, DISCUSSIONS.md and framework/ stay local; rules/, the other records and ada/ are published. The upload.sh workaround was reverted | DECISIONS.md 13 |
| 23 November 2026, 14:05 | Pushed rules, Ada scripts, records, ignore rules | Modular commits 663b04f, 2f7907d, a79cfba, d5fa5fb on Abhay | git log |
| 23 November 2026, 14:20 | T-Drive download blocked | Microsoft refuses scripted downloads (403); not worked around; asked the user to download in a browser | challenges.md 6 |
| 23 November 2026, 14:25 | Project venv | Created .venv (git-ignored) with osmnx and mlxtend, so the system Python is untouched | ENGINEERING.md |
| 23 November 2026, 14:40 | OSM download via Overpass failed (502) | Not retried in a loop; switched to the BBBike Beijing extract, prepare_osm.py rewritten to build from the file | challenges.md 7 |
| 23 November 2026, 20:00 | Road graph built from the BBBike extract | 34,135 intersections, 76,592 directed segments inside the 5th Ring box; output checked (extent, lengths, road types, one-way) | DATA.md "Road graph" |
| 24 November 2026, 11:30 | T-Drive found and extracted | The user saved the zip in the repo root; moved to data_raw/tdrive/, contents checked (official release), licence read: no redistribution of data or derivatives | DATA.md |
| 24 November 2026, 11:45 | T-Drive profiled and cleaned | 17.66M rows to 11.77M points inside the 5th Ring box, 10,207 taxis | DATA.md |
| 24 November 2026, 11:50 | Map-matching: the user chose Python | Benchmark leuvenmapmatching on a sample before committing to it | DECISIONS.md 15 |
| 24 November 2026, 12:40 | Map-matching benchmarked and smoke-tested | 95.5% of points matched; every matched step is a real directed road segment; about 2 to 4 min per taxi per core | DATA.md "Map-matching" |
| 24 November 2026, 13:05 | Main map-matching run started on the laptop | 1,000 random taxis, 7 workers, resumable chunks of 50 in data_clean/match_chunks/; expected 8 to 9 h | RESUME.md |
| 24 November 2026, 11:55 | **Correction to the times above** | The 23 November times were UTC labelled as IST (add 5 h 30 min: setup began about 18:37 IST). The 24 November times before this line were estimates; the T-Drive work ran from about 11:16 IST and the main map-matching run started at 11:46 IST. Times from here on are read from the Windows clock | challenges.md 8 |
| 24 November 2026, 11:55 | Transaction builder written and tested | Smoke sample: 350 transactions to 105 gap-free rows in a 4 km area with 100 columns; library tests pass (paper Figure 1 example reproduced) | DATA.md |
| 24 November 2026, 12:06 | The user asked to run map-matching on Ada | Ada checked: 7.3 GB free, queue empty. Added the time guard, data report, env.sbatch and match.sbatch (commits 9379226, 7244281, 11d4843). Waiting for the go to upload and submit (rules: show the sbatch before the first submission) | DECISIONS.md 18 |
| 24 November 2026, 12:17 | Uploaded to Ada and submitted the environment job 99351 | The user gave standing permission (no go needed); code 680d943 and data uploaded, MD5s recorded; watcher and monitor started | compute_log.md |
| 24 November 2026, 12:26 | Env job 99351 finished (COMPLETED, 9 min) | Log checked: imports and tests ok | compute_log.md |
| 24 November 2026, 12:31 | Submitted match job 99363; stopped the laptop run | No laptop chunk had finished, so nothing to upload | |
| 24 November 2026, 12:33 | 99363 failed in 0 s; the watcher resubmitted it as 99364 | Log read: missing torch in the project env, not a bad node. 99364 failed the same way in 0 s (scancel was blocked by the safety check) | challenges.md 9 |
| 24 November 2026, 12:37 | Fixed and resubmitted the env job as 99366 | Env now gets torch (CUDA 12.8) and the TabDiff packages; code 751d9bd uploaded | compute_log.md |
| 24 November 2026, 12:37 | Evaluation suite and baselines written | 15 tests pass, including the paper's worked example omega(p1) = 100 | commits 5212387 to 193342c |
| 24 November 2026, 12:58 | Env job 99366 finished (COMPLETED, 21 min) | Log checked: torch 2.11.0+cu128, CUDA kernel ok on the 2080 Ti, 15 tests pass. Env is 5.8 GB: Ada home at 95% (1.5 GB free) | compute_log.md |
| 24 November 2026, 12:59 | Submitted matching job 99378 | Same 1,000 taxis, resumable chunks | RESUME.md |
| 24 November 2026, 13:38 | New Claude session; background watcher, monitors and the laptop sampling test had stopped | Ada job 99378 still running (40 min, 2 of 20 chunks, ~16 min per chunk); watcher and monitor restarted; sampling test rerun | RESUME.md |
| 24 November 2026, 13:45 | Runner options for Ada | --skip-tabdiff-eval, --seed, --samples-out (decision 19) | DECISIONS.md 19 |
| 24 November 2026, 18:03 | Matching job 99378 ended (COMPLETED, 5.08 h) | Time guard stopped it after 17 of 20 chunks (26,206 pieces); log checked | compute_log.md |
| 24 November 2026, 18:07 | Submitted continuation 99794 | Last 3 chunks; watcher and monitor started | |
| 24 November 2026, 18:47 | Matching finished (99794 COMPLETED) | All 20 chunks, 30,246 pieces, 98.6% of points matched; copied to results_ada/match | DATA.md |
| 24 November 2026, 18:52 | Built tdrive_k300 (K=300, 4 km) | 42,705 rows (train 29,378), median 3 segments per row; uploaded with code 7eb99da | DATA.md |
| 24 November 2026, 18:55 | Submitted TabDiff training 99854 | 8,000 epochs max, checkpoint every 500, in-loop eval skipped (decision 19) | compute_log.md |
| 24 November 2026, 18:53 | Training 99854 failed at epoch 1 (32 s) | Pickling error under Python 3.14; fixed in a860ba9, uploaded | challenges.md 10 |
| 24 November 2026, 18:58 | Resubmitted training as 99856 | Watcher started; waiting for the first epoch timings | compute_log.md |
| 24 November 2026, 18:55 | Training 99856 failed: CUDA out of memory (batch 4096) | Added --train-batch-size; resubmitted with 1024 as 99857 | challenges.md 11 |
| 24 November 2026, 19:20 | 99857 trains: epoch 50 at 19:20, ~25 s per epoch | 8,000 epochs = ~55 h, too long. Own decision: 2,000 epochs (decision 20); cancelled 99857 (23 min) and submitted 99878 | DECISIONS.md 20 |
| 24 November 2026, 22:45 | Records updated for a chat compaction | Training 99878 at epoch ~350+, running; RESUME.md has the full restart state | RESUME.md |
