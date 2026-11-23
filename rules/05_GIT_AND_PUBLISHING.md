# 5. Git and publishing

## Commits

- Commit after every meaningful change: code, records, results or paper.
- Make modular commits: one purpose each, such as "records: job 81234 done" or "code: fix resume".
  Never mix unrelated changes in one commit.
- Messages: a short summary line in plain words, then details if needed.
- **No "Co-Authored-By: Claude" line and no Claude attribution, ever.**
- Run `git add` and `git commit` as separate commands. Check `git status` before each commit, and
  never commit secrets, data, tokens or large files.
- Push once the work is committed, unless the project's CLAUDE.md says the user pushes.

## What goes in git

| In git | Not in git (.gitignore) |
|---|---|
| Code, configs, tests, record files, analysis scripts | Raw and clean data, token caches, `out/`, `runs/` |
| Run summaries (`summary.json`, metrics CSVs), paper source and PDF, figures | Model checkpoints (`*.pt`), anything over 100 MB, `.claude/settings.local.json` |

Large files (models, checkpoints) are backed up outside GitHub: an external drive, Google Drive or a
private Hugging Face repo. GitHub LFS is not used. Its free tier is only 1 GB, and LFS files stay in the
repo history.

## Public code repo

The paper's code goes to a separate public repo, kept in a `public/` folder that the main repo ignores:

- it holds the code, configs, tests, the scripts that ran the jobs (with the account and QoS replaced
  by placeholders), the analysis scripts, and the run summaries;
- it does not hold the records (decisions, discussions, worklog), the paper, or any internal notes;
- remove internal references such as "decision 12" or "challenge 5" from it, then check by hand that
  the removal broke nothing (run the tests);
- it has its own README with how to run, dataset links with citations, the main results, and a
  LICENSE.

## Secrets

Never read, print or commit token files (`~/.kaggle/*`, SSH keys). Never put credentials in URLs or logs.
