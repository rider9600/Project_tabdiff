# Resume here: live state (updated 24 November 2026, 11:55 IST)

A new session reads CLAUDE.md, this file and the end of WORKLOG.md, then carries on with the queue below.

## 1. Where it stands

| Item | State |
|---|---|
| Running now | Ada: environment job 99351 (tdr_env), submitted 24 November 2026 12:17 IST. Laptop: map-matching of the same 1,000 taxis (7 workers, started 11:46 IST, chunks in data_clean/match_chunks/); it is stopped once the Ada matching job starts, and its finished chunks are uploaded to ~/tabdiff_roads/out/match/chunks |
| Watcher | scripts/ada_watch.py on job 99351 (laptop, background), log in the session scratchpad watch_log.jsonl; Monitor armed on it |
| Code on Ada | 680d943, uploaded 24 November 2026 12:16 IST, with tdrive_points.parquet and the road graph (MD5s in data_report.json) |
| Ada disk | 18 GB used of 25 GB (7.3 GB free) before the upload; project folder 133 MB |
| Laptop copies | None (no results_ada/ yet) |
| Compute used | 0 GPU h over 0 jobs |
| Git | Branch `Abhay`, last pushed commit 4259d73. Local-only files (CLAUDE.md, DECISIONS.md, DISCUSSIONS.md, framework/) are in `.git/info/exclude` |

## 2. Finished

| Part | Runs | GPU h | Where |
|---|---|---|---|
| Direction and public plan | none | 0 | docs/project_plan.md (pushed) |
| Framework placed | none | 0 | rules/, records, ada/, scripts/ada_watch.py |

## 3. Left, in this order

| Order | Module(s) | Contents | Predicted GPU h | Ready? |
|---|---|---|---|---|
| 0 | none | Open questions to the user: fabricated-results cleanup, decisions 9 and 10, empty report/ folder, GPU budget, teammate names | 0 | asked |
| 1 | laptop | OSM Beijing road graph and T-Drive download, profile, cleaning: **done** (DATA.md) | 0 | done |
| 2 | laptop | Map-matching: **running**. Next: backtracking transactions, area choice (≥ 20k transactions), TabDiff dataset files | 0 | in progress |
| 3 | laptop | Reddy et al. pipeline (FP-Growth, popularity, top-k), evaluation suite, baselines, tests | 0 | no |
| 4 | E0 | Environment job on Ada | 0.2 | no |
| 5 | E1 | Benchmark job: speed, memory, exact resume | 0.5 | no |
| 6 | E2 | Pilot training | to measure | no |
| 7 | E3 | Main training, split into 6 h jobs | to measure | no |
| 8 | E4 | Sampler comparison | small | no |

## 4. How to restart

1. Check `squeue` and `sacct` on Ada and `git status`.
2. Start a watcher for any running job, or submit the next ready module.
3. Before step 1 of the queue, make sure the open decisions have been answered.
