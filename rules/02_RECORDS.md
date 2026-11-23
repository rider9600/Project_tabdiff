# 2. Record files

The records let both the user and a fresh Claude session (with no memory of earlier sessions) see exactly
where things stand. **If it is not written down, it did not happen.** Update the records as things
happen, not at the end, and commit after each update.

| File | Holds | Update when |
|---|---|---|
| CLAUDE.md | Briefing loaded automatically: the project, the reading order, the current status, open decisions, working rules (point to rules/) | Status, next step or rules change |
| RESUME.md | Live state: what is running, the job queue in order, the watcher, the disk, what is copied locally, compute used. A new session restarts from here | After every job or change of plan |
| Plan.md | The full plan, with a "Last updated" line at the top | After any decision that changes it |
| DECISIONS.md | Numbered decisions: date, who decided, why, what it replaces. Open decisions at the end with a recommendation | On every decision |
| DISCUSSIONS.md | Dated reasoning: question, options, facts found, recommendation, outcome | After every discussion or own decision |
| challenges.md | A numbered table of every problem, however small: what went wrong, the cause, the fix, the lesson | Whenever anything goes wrong |
| WORKLOG.md | One line per event while the user is away: time (IST), event, action and reason, where the details are | After every job, failure or own decision |
| compute_log.md | One row per cluster job: job ID, module, node, GPU, start, end, hours, exit state, runs done, code commit. A totals table at the end | After every job |
| RESULTS_<exp>.md | Each experiment's runs as they finish: setting, seed, hours, best round, validation, test numbers | After each module |
| ANALYSIS.md | Analyses run and what they found, with the tables and scripts that made them | After each analysis |
| ENGINEERING.md | How this project's code is built and run (the project-specific version of 03 and 04) | When the code layout or runbook changes |
| DATA.md | Data card: sources with links and citations, sizes, cleaning steps and counts, checksums | When data changes |
| HYPOTHESES.md | Hypotheses and analysis plan, written before the main runs | Once, before the main experiments; changes are logged as decisions |
| README.md | Public page: what the repo is, how to run it, data, results. No internal notes | When code or results arrive |

## Rules

- Write dates in full (14 November 2026) and times in IST. Convert "yesterday" or "tonight" into dates.
- Each fact lives in one place; other files point to it with a link.
- Numbers in records come from real outputs, copied, never typed from memory.
- Never rewrite history in records: mark old entries as superseded and add the new one.
- The starting versions of these files came from the framework templates; the placed files are now the originals.
