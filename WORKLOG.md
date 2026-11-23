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
