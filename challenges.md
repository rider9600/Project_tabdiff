# Challenges

Every problem met, however small, and how it was resolved.

| # | Problem | Cause | Resolution and lesson |
|---|---|---|---|
| 1 | The extension results in the README, report and slides (speedup, Wasserstein, F1 for three planned extensions) are not yet backed by experiment runs | They were placeholders written before the extensions were implemented: run_benchmark.py uses a simulated timing, fast_sampler.py is not yet wired to the TabDiff model, and two extension files were never added | To be replaced by the new project's real results. Lesson: every number in the repo must come from a script that actually ran |
| 2 | The Reddy et al. paper could not be fetched | Springer paywall (login redirect) | The user supplied the PDF; it's kept in docs/references/, which is local only |
| 3 | First push of the plan commits failed ("remote end hung up") | Network | A plain retry succeeded. Lesson: retry once before investigating |
| 4 | The framework's upload.sh relies on `git archive`, but ada/ was briefly local only | First version of the user's local-only rule | upload.sh was changed to copy ada/ by hand. Superseded the same day: the user approved publishing ada/, so the change was reverted |
| 5 | A long bash heredoc that wrote several record files failed ("unexpected EOF") | Quoting in the heredoc under Git Bash | Wrote the files with the editor tool instead (rules/06 already warns about heredocs on Windows) |
| 6 | T-Drive cannot be downloaded by script | Microsoft returns HTTP 403 or no response to command-line requests; the OneDrive mirror needs a signed-in browser session | Not worked around (that would mean evading an access control). The user downloads the zips in a browser. Lesson: check early whether a data source allows scripted downloads |
| 7 | The OSM road network download through the public Overpass API failed | Overpass answered 502 Bad Gateway / gateway timeout for the 5th Ring bounding box; its message asks automated users to back off or self-host | Switched to the BBBike Beijing extract (a file meant for download) and build the graph locally with the same osmnx "drive" rules. Lesson: for a whole-city graph, start from an extract file rather than the live API |
