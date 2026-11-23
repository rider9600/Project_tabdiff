# 3. Ada HPC (IIIT Hyderabad)

Heavy compute runs on Ada through SLURM. The laptop (GTX 1650, 4 GB) does light work only: data
preparation, editing, tests, polling. **The admins are strict. Follow every rule here exactly. If you
are unsure whether something is allowed, put it inside a job.**

## Connection

- `ssh -i ~/.ssh/id_ed25519_ada -o BatchMode=yes cs9442.01@ada-gw1.iiit.ac.in`. Use the same key for
  scp. The laptop has no rsync. If gw1 is down, use `ada-gw2`.
- Home is `/home2/cs9442.01`, with a 25 GB quota shared with the user's other projects. Run `df -h ~`
  before every upload.
- Each project lives in `~/<project>/` with the folders `code/`, `data_clean/`, `out/<module>/` and
  `logs/`. Its environment is in `~/envs/<project>`.

## The gateway runs nothing

- **Allowed:** `ls`, `du`, `df`, `cat` or `head` of small files, `mkdir`, `rm` (only with the user's
  yes), scp, `sbatch`, `squeue`, `sacct`, `scancel`.
- **Never:** python, pip or conda, unzip, checksums, loops or `watch`, long or background commands,
  Jupyter.
- Check every ssh command against these lists. Send one short command per ssh call.

## Jobs

Every job is an sbatch file in the project's `ada/` folder. Start from
[ada/job.sbatch](../ada/job.sbatch) (or the renamed copy), which sources [ada/common.sh](../ada/common.sh).

- **Directives:** `--account=cs9442 --qos=cs9442 --partition=u22 --cpus-per-task=10 --gres=gpu:1
  --mem=28G --constraint=2080ti`, `--time` at most 06:00:00, the log path
  `~/<project>/logs/slurm_%x_%j.out`, and the exclude list of known bad nodes. Add to that list
  whenever a node fails, and log the node in challenges.md.
- **common.sh** prints the node, job ID, start time and code version. It checks the GPU
  (`nvidia-smi`, `torch.cuda.is_available()`, a tiny CUDA kernel) and exits at once on failure. It
  creates `/ssd_scratch/$USER/$SLURM_JOB_ID` with a trap that removes it, and sets
  `OMP_NUM_THREADS=1`.
- **Data check:** each job compares the uploaded data's MD5 against the laptop's value and stops on a
  mismatch.
- **One job at a time**, whether queued or running. Before submitting, state the expected runtime
  against the 6 h limit. If you are unsure of it, run a short benchmark job first.
- Keep `num_workers` at 8 or below. Keep checkpoints small, and delete intermediate checkpoints once a
  run finishes.

## Runbook

| Step | Where | What | Done when |
|---|---|---|---|
| 1 | Laptop | Prepare data, write `data_report.json` with MD5s | file written |
| 2 | Laptop | Commit, then `PROJECT=<p> bash ada/upload.sh <scratch dir>`. It uploads `git archive HEAD` with a VERSION file | `cat ~/<p>/code/VERSION` shows the commit |
| 3 | Ada job | Environment job: build the venv, import every module, run the unit tests, write `.ready` | log ends "env ready" |
| 4 | Ada job | Setup and benchmark: measure speed and memory, check that resume is exact | per-run speed known |
| 5 | Ada job | Experiment modules, one after another | `module_report.json` shows every run done |
| 6 | Laptop | Copy `~/<p>/out/<module>` to `results_ada/` (scp -r), check the outputs, update records, commit | every job has a row in compute_log.md |

Never upload while a job is running: the job could read half-copied code.

## Limits at a glance

| Limit | Value | How it is respected |
|---|---|---|
| Wall time per job | 6 h (`--time=06:00:00` maximum) | Modules planned at 5 h or less; runner's guard stops starting runs past 5.5 h; resubmit continues |
| Jobs at once | 1, queued or running | Check `squeue -u cs9442.01` is empty before every `sbatch`; the watcher refuses to resubmit if anything is queued |
| GPU / CPU / RAM | 1 GPU (RTX 2080 Ti, 11 GB), 10 CPUs, 28 GB | `--gres=gpu:1 --cpus-per-task=10 --mem=28G --constraint=2080ti`; `num_workers` at most 8 |
| Disk | 25 GB home, shared with the user's other projects | `df -h ~` before uploads; small checkpoints, intermediates deleted by the code after each run; never delete other files without a yes |
| Scratch | `/ssd_scratch/$USER/$SLURM_JOB_ID`, node-local | Created and removed by common.sh |
| Gateway | Runs nothing | Only the allowed commands, one short command per ssh call |
| GPU hours | The project's budget in Plan.md | Running total in compute_log.md after every job; warn the user at 80% |
| Bad nodes | Exclude list in every sbatch | Add a node after any infrastructure failure, and log it in challenges.md |

## Watcher and monitor (laptop only)

Two pieces work together. The **watcher** is a Python process on the laptop that polls Ada and handles
restarts. The **monitor** is Claude Code's Monitor tool, which wakes the agent when the watcher writes
an event, so the agent never has to poll or guess.

**1. Submit, then start the watcher at once**, as a background command (`run_in_background`), never in
the foreground:

```
PROJECT=<p> python scripts/ada_watch.py --job <id> --sbatch "<exact args given to sbatch>" --expect-min <minutes> --log <scratchpad>/watch_log.jsonl
```

- `--sbatch` must repeat the submission exactly, including `--export=...` and any `--exclude`, so a
  resubmission is identical. The watcher merges failed nodes into the existing `--exclude`.
- `--expect-min` is the predicted runtime. The watcher stops at 1.5 x that plus 2 h of queue time.
- It checks once at 2 minutes (most failures happen early), then every 5 minutes, one short ssh
  command per check (`squeue`, then `sacct` and `tail` of the log when the job leaves the queue).
  It never runs a loop on Ada.
- If both `squeue` and `sacct` return nothing, the network failed, not the job. It waits and asks
  again.
- One watcher per job. A new session must start its own watcher for any job already running.

**2. Arm a monitor on the watcher's log.** It writes one JSON line per event to `--log`:

| `event` | Meaning | What the agent does |
|---|---|---|
| `watch` | Watcher started | Nothing |
| `ended` | Job left the queue (has the sacct line) | Wait for the next line |
| `done` | Completed | One-line notice to the user at once, then check the outputs, copy them, record, submit the next job |
| `resubmitted` | TIMEOUT or infrastructure failure, resubmitted (old and new job IDs, excluded nodes) | Record in WORKLOG and compute_log (and challenges if it was a node); start a new watcher for the new job |
| `failed` | Code error or unsupported GPU; not resubmitted | Notify the user, read the log, fix, record in challenges.md, resubmit with a new watcher |
| `watch_deadline` | Stopped at its time limit | Check the job by hand (commands below) and decide |

Use the Monitor tool on that file with a pattern such as `"event": "(done|failed|resubmitted|watch_deadline)"`.
A monitor can expire, so **re-arm it every 30 minutes** for as long as a job is running, and re-arm it
straight away after any wake-up. Also schedule a long fallback wake-up (20 to 30 minutes) so that a
missed event still gets noticed. Never poll Ada in a tight loop from the agent itself.

**3. When a job ends**, always send the one-line notice to the user before checking anything (for
example "E2_04 finished 05:13, checking now"). Silence while checking looks like the end was missed.

Actions by ending:

| Ending | Action |
|---|---|
| Completed | Notify the user in one line. Check the real outputs, copy them to the laptop, update records, submit the next job |
| GPU check failed, CUDA error, NODE_FAIL, hang | Resubmit once with that node excluded. Log it in challenges.md |
| "no kernel image" (unsupported GPU) | Stop. The sbatch file needs fixing, not a resubmit |
| TIMEOUT | Resubmit. The code resumes from checkpoints |
| Code error | Stop. Fix the code (a commit, an upload, and the tests), record the fix in challenges.md, resubmit |

The watcher resubmits by itself at most twice for TIMEOUT and once for an infrastructure failure. After
that, it stops and the agent decides.

**Checking a job by hand** (each line is one allowed gateway command):

```
ssh -i ~/.ssh/id_ed25519_ada -o BatchMode=yes cs9442.01@ada-gw1.iiit.ac.in "squeue -u cs9442.01"
ssh -i ~/.ssh/id_ed25519_ada -o BatchMode=yes cs9442.01@ada-gw1.iiit.ac.in "sacct -j <job> -X -o JobID,JobName,State,ExitCode,Elapsed,NodeList"
ssh -i ~/.ssh/id_ed25519_ada -o BatchMode=yes cs9442.01@ada-gw1.iiit.ac.in "tail -n 40 ~/<project>/logs/slurm_<job name>_<job>.out"
```

## Kaggle (fallback and extra capacity)

- Kaggle provides 30 GPU hours a week per account.
- Push notebooks with the Kaggle API from the laptop.
- Never exceed the quota.
- Copy each finished notebook's output to `results_kaggle/`.
- Record each notebook in compute_log.md like an Ada job.
