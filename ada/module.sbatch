#!/bin/bash
# Template for every Ada job (rules/03_ADA_HPC.md). Placed copy for this project (PROJECT=tabdiff_roads, prefix tdr).
# Submit with
#     sbatch --export=ALL,PROJECT=tabdiff_roads,MODULE=<name> tabdiff_roads/code/ada/module.sbatch
# Finished runs must be skipped and unfinished ones resumed, so resubmitting continues the work.
#SBATCH --job-name=tdr_module
#SBATCH --account=cs9442
#SBATCH --qos=cs9442
#SBATCH --partition=u22
#SBATCH --cpus-per-task=10
#SBATCH --gres=gpu:1
#SBATCH --constraint=2080ti        # torch built for CUDA 12.8 needs sm_75+; GTX 1080 Ti (sm_61) fails
#SBATCH --mem=28G
#SBATCH --time=06:00:00
#SBATCH --exclude=gnode004,gnode066,gnode061,gnode044,gnode068,gnode054,gnode079,gnode091,gnode053,gnode069,gnode076
#SBATCH --output=/home2/cs9442.01/tabdiff_roads/logs/slurm_%x_%j.out

set -euo pipefail
: "${PROJECT:?set PROJECT with --export=ALL,PROJECT=<project>}"
: "${MODULE:?set MODULE with --export=ALL,MODULE=<name>}"
source /home2/cs9442.01/$PROJECT/code/ada/common.sh
[ -f "$HOME/envs/$PROJECT/.ready" ] || { echo "~/envs/$PROJECT not ready: run the env job first"; exit 1; }
echo "=== module $MODULE"

# The project's own runner. It must: skip finished runs, resume from checkpoints, stop starting
# new runs when elapsed + 1.2 x predicted > 5.5 h, and write out/$MODULE/module_report.json.
python scripts/run_module.py --module "$MODULE" --out-dir "$PROJ/out/$MODULE" --session-start "$JOB_START"
