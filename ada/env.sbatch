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
export USE_QM_ENV=1                                      # GPU check with ~/envs/qm while building
source /home2/cs9442.01/$PROJECT/code/ada/common.sh

ENV=$HOME/envs/$PROJECT
if [ ! -x "$ENV/bin/python" ]; then
    python -m venv "$ENV"
fi
set +u; source "$ENV/bin/activate"; set -u
python -m pip install -q --upgrade pip
python -m pip install -q -r requirements_match.txt
# PyTorch with CUDA 12.8 (supports the RTX 2080 Ti, sm_75), then the TabDiff packages.
python -m pip install -q torch --index-url https://download.pytorch.org/whl/cu128
python -m pip install -q -r requirements_tabdiff.txt
python -c "import osmnx, leuvenmapmatching, rtree, pyproj, pandas, pyarrow, mlxtend; print('imports ok', osmnx.__version__)"
python -c "import torch, sklearn, scipy, sdmetrics, xgboost, tomli, tomli_w, prdc, icecream, category_encoders; print('tabdiff imports ok, torch', torch.__version__)"
# The project env itself must run a CUDA kernel on this GPU, since common.sh checks the GPU with it.
python -c "import torch; x = torch.ones(8, device='cuda'); assert float((x * 2).sum()) == 16; print('cuda ok', torch.cuda.get_device_name(0))"
python -m unittest discover -s tests -v
du -sh "$ENV"
touch "$ENV/.ready"
echo "env ready"
