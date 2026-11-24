# Resume here: live state (updated 23 November 2026, 13:15 IST)

A new session reads CLAUDE.md, this file and the end of WORKLOG.md, then carries on with the queue below.

## 1. Where it stands

| Item | State |
|---|---|
| Running now | Laptop: map-matching of 1,000 taxis (scripts/match_tdrive.py, 7 workers), started 24 November 2026 13:05 IST, log data_clean/match_run.log, resumable: rerun the same command to continue |
| Watcher | None |
| Code on Ada | None uploaded. Folder `~/tabdiff_roads` not yet created |
| Ada disk | Not checked yet (`df -h ~` before the first upload) |
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
