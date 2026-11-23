# 7. The session loop

## Start of every session

1. Read CLAUDE.md (loaded automatically), then RESUME.md, then the end of WORKLOG.md.
2. Read rules/ if you have not yet done so in this session.
3. Check the live state yourself rather than trusting the records alone: `squeue` and `sacct` on Ada,
   `git status`, and the latest outputs.
4. If a job is running, start a watcher for it and arm a monitor on the watcher log (rules/03_ADA_HPC.md, "Watcher and monitor"). If nothing is running and the queue has ready work,
   submit the next job.

## During work

```
submit job -> start watcher + arm monitor (re-arm every 30 min) -> while it runs: write next code / analysis / records
job ends   -> one-line notice to the user -> check real outputs -> copy to laptop
           -> update compute_log, RESULTS_*, RESUME, WORKLOG (+ challenges if anything went wrong)
           -> commit -> submit next job
```

- On any decision: write it to DECISIONS.md, DISCUSSIONS.md and WORKLOG.md, and update Plan.md if the
  decision changes the plan.
- On any problem: add it to challenges.md, then fix it or route around it, and keep going.
- Keep RESUME.md good enough that a new session could take over at any moment.

## When the user returns

Report from WORKLOG.md in this order:

1. **Decisions taken on your own**, as a table: decision, why, effect, whether it can be undone. Ask for
   confirmation.
2. Jobs finished and the main results, including unfavorable ones.
3. Problems met and how they were handled.
4. What is running now, and what comes next.

Keep it short, with tables. Details stay in the record files, with links.

## Before the context runs out

Update RESUME.md and CLAUDE.md's status, and commit, so that the next session starts cleanly.
