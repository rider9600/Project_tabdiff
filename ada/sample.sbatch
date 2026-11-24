#!/bin/bash
# TabDiff sampling job (module "sample"). For every checkpoint listed in EPOCHS, every sampler in
# SAMPLERS (default, graph) and every seed in SEEDS, generates one synthetic table and writes it to
# $PROJ/out/sample/$NAME/$EXP/<sampler>_e<epoch>_s<seed>.csv. Tables that already exist are skipped,
# so a job that hits the time limit can simply be resubmitted. Submit with
#     sbatch --export=ALL,PROJECT=tabdiff_roads,NAME=tdrive_k300,EXP=e2000,EPOCHS="500 750",SEEDS=0 \
#         tabdiff_roads/code/ada/sample.sbatch
#SBATCH --job-name=tdr_sample
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
: "${PROJECT:?set PROJECT}"; : "${NAME:?set NAME}"; : "${EPOCHS:?set EPOCHS}"
EXP=${EXP:-main}; SEEDS=${SEEDS:-0}; SAMPLERS=${SAMPLERS:-"default graph"}; STRENGTH=${STRENGTH:-0.5}
source /home2/cs9442.01/$PROJECT/code/ada/common.sh
[ -f "$HOME/envs/$PROJECT/.ready" ] || { echo "~/envs/$PROJECT not ready: run the env job first"; exit 1; }
export WANDB_MODE=disabled PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True

python scripts/register_tabdiff_dataset.py --name "$NAME" --src "$PROJ/data_clean/tabdiff/$NAME"
CKPT_DIR=baseline_tabdiff/tabdiff/ckpt/$NAME/$EXP
mkdir -p "$(dirname "$CKPT_DIR")" "$PROJ/out/sample/$NAME/$EXP"
[ -L "$CKPT_DIR" ] || ln -s "$PROJ/out/train/$NAME/$EXP" "$CKPT_DIR"
EDGES="$PROJ/data_clean/tabdiff/$NAME/edges.csv"

for E in $EPOCHS; do
  CK="$PROJ/out/train/$NAME/$EXP/model_$E.pt"
  [ -f "$CK" ] || { echo "=== missing $CK, skipped"; continue; }
  for S in $SEEDS; do
    for SM in $SAMPLERS; do
      OUT="$PROJ/out/sample/$NAME/$EXP/${SM}_e${E}_s${S}.csv"
      [ -f "$OUT" ] && { echo "=== exists $OUT"; continue; }
      G=(); [ "$SM" = graph ] && G=(--graph-edges "$EDGES" --graph-strength "$STRENGTH")
      T0=$(date +%s)
      python -u scripts/run_tabdiff.py "${G[@]}" --skip-tabdiff-eval --seed "$S" --sample-batch-size 2000 \
          --samples-out "$OUT" -- --dataname "$NAME" --mode test --ckpt_path "$CK" --no_wandb --exp_name "$EXP"
      echo "=== done $OUT in $(( $(date +%s) - T0 )) s"
    done
  done
done
ls -la "$PROJ/out/sample/$NAME/$EXP"
