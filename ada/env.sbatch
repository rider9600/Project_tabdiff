#!/bin/bash
# Environment job (rules/03 runbook step 3): build ~/envs/tabdiff_roads, import every module, run the
# unit tests, and write .ready. Submit with
#     sbatch --export=ALL,PROJECT=tabdiff_roads tabdiff_roads/code/ada/env.sbatch
#SBATCH --job-name=tdr_env
#SBATCH --account=cs9442
#SBATCH --qos=cs9442
#SBATCH --partition=u22
#SBATCH --cpus-per-task=10
#SBATCH --gres=gpu:1
#SBATCH --constraint=2080ti
#SBATCH --mem=28G
#SBATCH --time=01:00:00
#SBATCH --exclude=gnode004,gnode066,gnode061,gnode044,gnode068,gnode054,gnode079,gnode091,gnode053,gnode069,gnode076
#SBATCH --output=/home2/cs9442.01/tabdiff_roads/logs/slurm_%x_%j.out

set -euo pipefail
: "${PROJECT:?set PROJECT with --export=ALL,PROJECT=tabdiff_roads}"
source /home2/cs9442.01/$PROJECT/code/ada/common.sh     # activates ~/envs/qm until .ready exists

ENV=$HOME/envs/$PROJECT
if [ ! -x "$ENV/bin/python" ]; then
    python -m venv "$ENV"
fi
set +u; source "$ENV/bin/activate"; set -u
python -m pip install -q --upgrade pip
python -m pip install -q -r requirements_match.txt
python -c "import osmnx, leuvenmapmatching, rtree, pyproj, pandas, pyarrow, mlxtend; print('imports ok', osmnx.__version__)"
python -m unittest discover -s tests -v
du -sh "$ENV"
touch "$ENV/.ready"
echo "env ready"
