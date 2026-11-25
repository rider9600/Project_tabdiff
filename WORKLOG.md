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
| 25 November 2026, 01:21 | Training 99878 hit the 6 h limit (TIMEOUT) at ~epoch 770 | Watcher crashed (decoding); fixed; resubmitted as 100223 from model_500 with checkpoints every 250 epochs | challenges.md 13 |
| 25 November 2026 | The user proposed generating GPS coordinates directly | Recorded as a possible comparison (DiffTraj-style coordinate encoding); open for discussion | DISCUSSIONS.md, Plan.md 7 |
| 25 November 2026, 02:15 | Records updated for a chat compaction | Training 100223 at epoch 600/2000, loss 0.44; RESUME.md current | RESUME.md |

## 25 November 2026, 11:45 IST
- 100223 hit TIMEOUT at 07:24 (epoch ~1260; checkpoints 750, 1000, 1250); watcher resubmitted as 100439 (07:27, gnode049).
- 11:43: 100439 at epoch 1797/2000, loss ~1.05 total (DLoss 0.07); checkpoints up to 1750. Expected end ~13:20, just inside the 6 h limit (13:27); if it times out, the watcher resubmits and the last epochs take minutes.
- ada/sample.sbatch written and pushed (3246067). Laptop CPU check of sampling with model_1750 and the graph-aware sampler (2,000 rows) running, to catch bugs before the Ada sampling job.

## 25 November 2026, 12:00 IST: first look at generated transactions (laptop, CPU)
- model_1750, graph-aware sampler (strength 0.5), seed 0, 2,000 rows: sampling took 768 s on the CPU (798 s wall-clock). The pipeline works end to end.
- Synthetic rows are far too short: 0.78 segments per row on average, against 4.33 in real val; 25.9% of rows are empty. Of the non-empty rows, most are single segments, so "valid" 71.5% is inflated by trivial rows. Gaps 2.7%, branches and cycles 0%.
- Busy roads: Spearman 0.58 between real and synthetic segment use; top-10 overlap 0.4, top-50 0.52.
- The graph-aware sampler flagged only 0.1% of segments per re-masking step: with so few active segments, there are few gaps or branches for it to act on.
- Reading: the model under-generates the rare "present" value of the 300 sparse binary columns. This is a finding to report; possible fixes (conditioning on trip length, re-weighting the present class) are design changes, to discuss with the user (open item O7).

## 25 November 2026, 13:20 IST
- Training COMPLETED (100439, 13:18): 2,000 epochs, checkpoints every 250 from 500 to 2000. Total 17.85 GPU hours over 3 jobs.
- Watcher crashed again when printing tqdm characters to the Windows console (cp1252); fixed with UTF-8 stdout (9435484). Challenge 14.
- Sampling job 100792 submitted: 7 checkpoints x {default, graph-aware 0.5}, seed 0, 4,566 rows each (validation size).

## 25 November 2026, 14:50 IST: checkpoint sweep on validation (job 100792, 82 min, 14 tables)
- Each table 4,566 rows; 322 to 372 s per table on the 2080 Ti. Scores from scripts/select_checkpoint.py (22 s); full table in results_ada/sample/e2000/selection.json.
- **Correction of the 12:00 reading:** the short rows came from the graph-aware sampler, not from the model. The default sampler matches real row length (4.3 vs 4.33 segments).
- Default sampler: epochs 500-750 are 60% drivable, gaps 38%, recover 8.7% of real multi-segment frequent itemsets, busy-road Spearman 0.57-0.78. From epoch 1000 on: 6% drivable, gaps 91%, no frequent itemsets, Spearman ~0.81. Longer training improved per-segment frequencies but broke the joint structure within rows.
- Graph-aware sampler (0.5): 96-97% of non-empty rows drivable, gaps 2-3%, but rows are short (2.0 segments at 500-750, 0.8 from 1000 on, with 25% empty) and no frequent itemsets. It trades length for validity.
- Selection score picks default @ 750 and graph @ 1750. Next: tune graph strength (0.1, 0.25) at epoch 750 on validation (jobs 100888 and one more), then the final 3-seed run on test.

## 25 November 2026, 15:00 IST: strength tuning (val, epoch 750) and final run
- 100888 (strength 0.1, 6.9 min) and 100893 (0.25, 6.6 min). Results: 0.1 -> 2.56 segments/row, 88% of non-empty rows drivable, Spearman 0.43; 0.25 -> 2.20, 94%, 0.23; 0.5 -> 2.01, 97%, 0.14. No setting recovers frequent itemsets. Chosen: 0.1 (decision 23).
- Final sampling job 100904 submitted 15:01: epoch 750, {default, graph-aware 0.1} x seeds 10, 11, 12, 8,761 rows each.

## 25 November 2026, 16:40 IST: final evaluation (laptop, 297 s)
- Test split, 8,761 rows per table, 3 seeds each for TabDiff. Results in docs/results_tdrive.md; raw in results_ada/final/evaluation.json.
- Popular-path evaluation fixed: queries were never found by random probing (0 queries); now enumerated (26 pairs, one per distinct set of alternatives). With minF = 423 every candidate path has a segment below minF, so Reddy et al.'s omega is 0 everywhere; added omega without the minF rule (decision 25).
- Headline: TabDiff default 61% drivable, Spearman 0.81, itemset Jaccard 0.10; graph-aware 0.1 87% drivable, 2.57 segments/row, Spearman 0.52; Markov baseline best on fidelity.

## 25 November 2026, 17:45 IST: ablation arm B (job 101112, 35 min; evaluation 432 s)
- Random re-masking (count matched to the graph rule's flags in the current state, random decided segments): 62.6% drivable, 3.85 segments/row, Spearman 0.81; re-masked share 0.49% per step (graph-aware 0.16%).
- vs A (no re-masking) 61.0% and C (graph-aware) 87.0%. The validity gain comes from the graph targeting. Written into docs/results_tdrive.md.

## 25 November 2026, 21:00 IST: DiffTraj comparison started (agreed with the user: options B and C)
- DiffTraj code vendored (MIT, upstream 27d25a9); authors' Chengdu checkpoint downloaded on Ada (md5 cfd3c57e...).
- Export: the same transactions as TabDiff (train 29,378 / val 4,566 / test 8,761) as 200-point trips with DiffTraj's 8 attributes (time fields 0). 16 s.
- Decoder (map-matching back to the 300 columns), checked on 300 real val trips: Jaccard 0.94, exact rows 77%, 4.64 vs 4.40 segments per row. This is the ceiling for DiffTraj after decoding.
- Batch 1024 and 512 ran out of memory on the 2080 Ti; kept the authors' batch 1024 with gradient accumulation (8 x 128). Ada home 98% full: checkpoints on node scratch, only final weights (65 MB) kept.
- Job 101372 (B, fine-tune 50 epochs): 55 s per epoch, loss 0.023 -> 0.006 after 2 epochs. C (200 epochs, ~3.1 h) next.

## 25 November 2026, 22:45 IST: DiffTraj B (fine-tuned) evaluated on test
- Decoding: ~10 min per seed (599-621 s), 99.8% of points matched, 7.8% empty rows (trips on roads outside the 300 columns).
- Test (mean of 3 seeds): drivable 83.8% (91% of non-empty), gaps 8.3%, 3.86 segments/row, busy-road Spearman 0.62, top-25 0.48, itemset Jaccard 0.335, maximal patterns contiguous 84%, tau (no minF) 0.50, exact copies 63%, DCR closer to train 8.5% (TabDiff 3.6%).
- Caveat: map-matching returns a connected road path, so part of DiffTraj's drivability comes from the decoder; its gaps only arise where the path leaves and re-enters the 300 columns.
- Evaluation run 438 s.
