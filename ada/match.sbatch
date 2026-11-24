#!/bin/bash
# Map-matching job (module "match"): matches the 1,000 sampled taxis in chunks of 50, saved to
# ~/tabdiff_roads/out/match/chunks. Finished chunks are skipped and the time guard stops starting new
# chunks near 5.5 h, so resubmitting the same command continues the work. Submit with
#     sbatch --export=ALL,PROJECT=tabdiff_roads tabdiff_roads/code/ada/match.sbatch
#SBATCH --job-name=tdr_match
#SBATCH --account=cs9442
#SBATCH --qos=cs9442
#SBATCH --partition=u22
#SBATCH --cpus-per-task=10
#SBATCH --gres=gpu:1
#SBATCH --constraint=2080ti
#SBATCH --mem=28G
#SBATCH --time=06:00:00
#SBATCH --exclude=gnode004,gnode066,gnode061,gnode044,gnode068,gnode054,gnode079,gnode091,gnode053,gnode069,gnode076
#SBATCH --output=/home2/cs9442.01/tabdiff_roads/logs/slurm_%x_%j.out

set -euo pipefail
: "${PROJECT:?set PROJECT with --export=ALL,PROJECT=tabdiff_roads}"
source /home2/cs9442.01/$PROJECT/code/ada/common.sh
[ -f "$HOME/envs/$PROJECT/.ready" ] || { echo "~/envs/$PROJECT not ready: run the env job first"; exit 1; }

# Data check: the uploaded files must have the laptop's MD5s (data_report.json).
python - <<'PY'
import hashlib, json, sys
from pathlib import Path
d = Path.home() / "tabdiff_roads" / "data_clean"
rep = json.loads((d / "data_report.json").read_text())
for name, info in rep["files"].items():
    h = hashlib.md5()
    with open(d / name, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    ok = h.hexdigest() == info["md5"]
    print(f"md5 {name}: {'ok' if ok else 'MISMATCH'}")
    if not ok:
        sys.exit(1)
PY

OUT=$PROJ/out/match
mkdir -p "$OUT/chunks"
python scripts/match_tdrive.py --taxis 1000 --seed 0 --workers 8 \
    --points "$PROJ/data_clean/tdrive_points.parquet" \
    --graph "$PROJ/data_clean/beijing_5th_ring_drive.graphml" \
    --chunk-dir "$OUT/chunks" --out "$OUT/matched_traversals.parquet" \
    --time-limit-h 5.5 --session-start "$JOB_START"
ls "$OUT/chunks" | grep -c '\.parquet$' | xargs echo "chunks done:"
