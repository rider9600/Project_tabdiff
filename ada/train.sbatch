#!/bin/bash
# TabDiff training job (module "train"). Registers the transaction table with TabDiff (once), then
# trains, resuming from the newest model_<epoch>.pt checkpoint if one exists. TabDiff saves a
# checkpoint every CHECK epochs, so a job that hits the 6 h limit (TIMEOUT) loses at most CHECK epochs;
# the watcher resubmits it and training continues. Submit with
#     sbatch --export=ALL,PROJECT=tabdiff_roads,NAME=tdrive_k300,STEPS=8000,CHECK=500,EXP=main \
#         tabdiff_roads/code/ada/train.sbatch
#SBATCH --job-name=tdr_train
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
: "${PROJECT:?set PROJECT}"; : "${NAME:?set NAME}"; : "${STEPS:?set STEPS}"; : "${CHECK:?set CHECK}"
EXP=${EXP:-main}
source /home2/cs9442.01/$PROJECT/code/ada/common.sh
[ -f "$HOME/envs/$PROJECT/.ready" ] || { echo "~/envs/$PROJECT not ready: run the env job first"; exit 1; }
export WANDB_MODE=disabled PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True

# Data check: the transaction table must match its laptop MD5s.
python - "$PROJ/data_clean/tabdiff/$NAME" <<'PY'
import hashlib, json, sys
from pathlib import Path
d = Path(sys.argv[1])
rep = json.loads((d / "md5.json").read_text())
for name, md5 in rep.items():
    ok = hashlib.md5((d / name).read_bytes()).hexdigest() == md5
    print(f"md5 {name}: {'ok' if ok else 'MISMATCH'}")
    if not ok:
        sys.exit(1)
PY

# TabDiff reads data and writes checkpoints inside its own tree; keep both in the project folder.
python scripts/register_tabdiff_dataset.py --name "$NAME" --src "$PROJ/data_clean/tabdiff/$NAME"
CKPT_DIR=baseline_tabdiff/tabdiff/ckpt/$NAME/$EXP
mkdir -p "$PROJ/out/train/$NAME/$EXP" "$(dirname "$CKPT_DIR")"
[ -L "$CKPT_DIR" ] || ln -s "$PROJ/out/train/$NAME/$EXP" "$CKPT_DIR"

LATEST=$(ls "$PROJ/out/train/$NAME/$EXP"/model_*.pt 2>/dev/null | sed -E 's/.*model_([0-9]+)\.pt/\1 &/' | sort -n | tail -1 | cut -d' ' -f2 || true)
RESUME=()
if [ -n "${LATEST:-}" ]; then
    echo "=== resuming from $LATEST"
    RESUME=(--ckpt_path "$LATEST")
fi
python -u scripts/run_tabdiff.py --skip-tabdiff-eval --train-batch-size "${BATCH:-1024}" --sample-batch-size 2000 -- --dataname "$NAME" --mode train --steps "$STEPS" \
    --check_val_every "$CHECK" --no_wandb --exp_name "$EXP" "${RESUME[@]}"
ls -la "$PROJ/out/train/$NAME/$EXP" | tail -5
