#!/bin/bash
# DiffTraj comparison job (module "difftraj"): train on our exported trips, then sample SEEDS x NSAMP
# trajectories. EXP=finetune with INIT=<authors' model.pt> starts from the Chengdu checkpoint (option B);
# EXP=scratch without INIT trains from random weights (option C). The resume checkpoint lives on the
# node's local scratch; only model_final.pt (about 65 MB) and the samples go to the home folder.
#     sbatch --export=ALL,PROJECT=tabdiff_roads,NAME=tdrive_k300,EXP=finetune,EPOCHS=50,\
#         INIT=/home2/cs9442.01/tabdiff_roads/pretrained/difftraj/model.pt tabdiff_roads/code/ada/difftraj.sbatch
#SBATCH --job-name=tdr_difftraj
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
: "${PROJECT:?set PROJECT}"; : "${NAME:?set NAME}"; : "${EXP:?set EXP}"; : "${EPOCHS:?set EPOCHS}"
INIT=${INIT:-}; BATCH=${BATCH:-512}; SEEDS=${SEEDS:-"10 11 12"}; NSAMP=${NSAMP:-8761}
source /home2/cs9442.01/$PROJECT/code/ada/common.sh
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
[ -f "$HOME/envs/$PROJECT/.ready" ] || { echo "~/envs/$PROJECT not ready: run the env job first"; exit 1; }

# The code reads data_clean/difftraj/<name> inside the code tree; link the uploaded copy there.
mkdir -p data_clean
[ -e data_clean/difftraj ] || ln -s "$PROJ/data_clean/difftraj" data_clean/difftraj
WORK=$S   # node-local scratch made by common.sh, removed when the job ends
OUT=$PROJ/out/difftraj

if [ ! -f "$OUT/$NAME/$EXP/model_final.pt" ]; then
  I=(); [ -n "$INIT" ] && I=(--init "$INIT")
  python -u scripts/run_difftraj.py train --name "$NAME" --exp "$EXP" --epochs "$EPOCHS" --check 10 --batch-size "$BATCH" \
      --work "$WORK" --out-root "$OUT" "${I[@]}"
fi
for SEED in $SEEDS; do
  [ -f "$OUT/$NAME/$EXP/samples_s$SEED.npy" ] && { echo "=== exists samples_s$SEED"; continue; }
  python -u scripts/run_difftraj.py sample --name "$NAME" --exp "$EXP" --seed "$SEED" --n "$NSAMP" --out-root "$OUT"
done
ls -la "$OUT/$NAME/$EXP"; df -h ~ | tail -1
