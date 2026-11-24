"""Laptop-side watcher for one Ada job (never runs on Ada). One short ssh command per poll.

    python ada_watch.py --job <id> --sbatch "<sbatch args as submitted>" --expect-min 40 \
        --log D:/Fedblacx/compute_log_watch.jsonl

- Polls squeue every 7 minutes; when the job leaves the queue, reads sacct and the log tail.
- Infrastructure failure (NODE_FAIL, GPU check failed, CUDA error, hang): resubmits once, with
  that node added to --exclude.
- TIMEOUT: resubmits (the code resumes from checkpoints), at most twice.
- Code error: stops and prints the error lines; no resubmit.
- Overall stop: 1.5 x expected runtime + 2 h queue allowance.
Each event is appended as one JSON line to --log, for the compute log.
"""

import argparse
import json
import os
import re
import subprocess
import sys
import time

PROJECT = os.environ.get("PROJECT") or sys.exit("set PROJECT (the folder under ~ on Ada)")
SSH = ["ssh", "-i", "~/.ssh/id_ed25519_ada", "-o", "BatchMode=yes", "-o", "ConnectTimeout=30",
       f"cs9442.01@{os.environ.get('ADA_GW', 'ada-gw1')}.iiit.ac.in"]   # ADA_GW=ada-gw2 when gw1 is down 
POLL_S = 300          # every 5 minutes
FIRST_S = 120         # one early check: most failures happen in the first minutes
INFRA = re.compile(r"GPU CHECK FAILED|CUDA error|no CUDA-capable|NODE_FAIL|"
                   r"cudaErrorDevicesUnavailable|uncorrectable ECC|Bus error|"
                   r"ssd_scratch.*No space left on device", re.I) 


def ssh(cmd: str) -> str:
    # UTF-8 with replacement: log tails contain progress-bar characters that the Windows default
    # code page cannot decode, which crashed the watcher when job 99878 ended (challenge 13).
    r = subprocess.run(SSH + [cmd], capture_output=True, text=True, encoding="utf-8", errors="replace",
                       timeout=120)
    return (r.stdout or "").strip()


def log(path, **kw):
    kw["time"] = time.strftime("%Y-%m-%d %H:%M:%S")
    print(json.dumps(kw), flush=True)
    with open(path, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(kw) + "\n")


BASE_EXCLUDE = "gnode004,gnode066,gnode061,gnode044,gnode068,gnode054,gnode079,gnode091,gnode053,gnode069,gnode076"


def with_exclude(args: str, nodes: list[str]) -> str:
    """sbatch keeps only the last --exclude, so merge the failed nodes into the one already in
    the arguments (or add one) instead of putting a second flag in front."""
    if not nodes:
        return args
    m = re.search(r"--exclude=(\S+)", args)
    if m:
        have = m.group(1).split(",")
        merged = ",".join(have + [n for n in nodes if n not in have])
        return args[:m.start(1)] + merged + args[m.end(1):]
    return f"--exclude={BASE_EXCLUDE},{','.join(nodes)} {args}"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--job", required=True)
    ap.add_argument("--sbatch", required=True, help="arguments after 'sbatch', e.g. '<project>/code/ada/setup.sbatch'")
    ap.add_argument("--expect-min", type=float, required=True)
    ap.add_argument("--log", required=True)
    a = ap.parse_args()
    deadline = time.time() + 60 * (1.5 * a.expect_min + 120)
    job, infra_retries, timeout_retries, exclude = a.job, 0, 0, []
    log(a.log, event="watch", job=job, expect_min=a.expect_min)
    time.sleep(FIRST_S)
    while time.time() < deadline:
        q = ssh(f"squeue -u cs9442.01 -h -j {job} -o '%i %T %M %R'")
        if q:
            print(time.strftime("%H:%M"), q, flush=True)
            time.sleep(POLL_S)
            continue
        acct = ssh(f"sacct -j {job} -X -n -P -o JobID,JobName,State,ExitCode,Elapsed,NodeList,Start,End")
        if not acct or "RUNNING" in acct or "PENDING" in acct:
            # Empty squeue and sacct together means the ssh call failed (network), not that the job
            # ended: wait and ask again.
            print(time.strftime("%H:%M"), "no answer from Ada or job still listed; retrying", flush=True)
            time.sleep(POLL_S)
            continue
        name = acct.split("|")[1] if "|" in acct else "job"
        tail = ssh(f"tail -n 40 ~/{PROJECT}/logs/slurm_{name}_{job}.out")
        state = acct.split("|")[2] if acct.count("|") >= 2 else "UNKNOWN"
        node = acct.split("|")[5] if acct.count("|") >= 5 else ""
        log(a.log, event="ended", job=job, sacct=acct)
        if state.startswith("COMPLETED"):
            print(tail)
            log(a.log, event="done", job=job)
            return 0
        retry = None
        if re.search(r"no kernel image|not compatible with the current PyTorch", tail):
            print("=== STOPPED: GPU type not supported by this torch (not a bad node; fix the sbatch). Log tail:")
            print(tail)
            log(a.log, event="failed", job=job, state=state, reason="unsupported GPU type")
            return 1
        if state.startswith("TIMEOUT") and timeout_retries < 2:
            timeout_retries += 1
            retry = "timeout"
        elif (state.startswith("NODE_FAIL") or INFRA.search(tail)) and infra_retries < 1:
            infra_retries += 1
            retry = "infrastructure"
            if node:
                exclude.append(node)
        if retry is None:
            print("=== STOPPED: job failed (not resubmitted). Log tail:\n" + tail)
            log(a.log, event="failed", job=job, state=state)
            return 1
        if ssh("squeue -u cs9442.01 -h -o %i"):
            print("=== another job is in the queue; not resubmitting")
            return 1
        out = ssh(f"sbatch {with_exclude(a.sbatch, exclude)}")
        m = re.search(r"Submitted batch job (\d+)", out)
        if not m:
            print("=== resubmit failed:", out)
            return 1
        log(a.log, event="resubmitted", reason=retry, old=job, new=m.group(1), exclude=exclude)
        job = m.group(1)
    log(a.log, event="watch_deadline", job=job)
    print("=== watcher reached its overall stop; check the job by hand")
    return 2


if __name__ == "__main__":
    sys.exit(main())
