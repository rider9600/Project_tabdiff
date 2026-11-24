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
