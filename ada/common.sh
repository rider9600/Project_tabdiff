# Sourced by every sbatch file in ada/ (rules/03_ADA_HPC.md). Runs on the compute node only.
# Prints where the job runs, checks the GPU, activates the Python env, makes job scratch.

PROJ=/home2/cs9442.01/${PROJECT:?set PROJECT}
JOB_START=$(date +%s)
echo "=== job ${SLURM_JOB_ID:-none} (${SLURM_JOB_NAME:-}) on $(hostname) start $(date '+%F %T')"

# The env: ~/envs/$PROJECT once ada/env.sbatch has checked it (.ready), else ~/envs/qm for the GPU check.
# The env job sets USE_QM_ENV=1 so that it always checks the GPU with ~/envs/qm while it (re)builds.
set +u   # activate scripts may read unset variables
if [ -f "$HOME/envs/$PROJECT/.ready" ] && [ -z "${USE_QM_ENV:-}" ]; then
    source "$HOME/envs/$PROJECT/bin/activate"
else
    source "$HOME/envs/qm/bin/activate"
fi
set -u
echo "=== python: $(command -v python)"

# GPU check: exit at once on a broken node (the watcher on the laptop resubmits without it).
timeout 60 nvidia-smi -L || echo "nvidia-smi failed"
timeout 120 python -c "import torch,sys; sys.exit(0 if torch.cuda.is_available() else 1)" || { echo "GPU CHECK FAILED on $(hostname)"; exit 1; }
timeout 120 python -c "import torch; x = torch.ones(8, device='cuda'); assert float((x * 2).sum()) == 16" \
    || { echo "GPU CHECK FAILED on $(hostname): a CUDA kernel did not run (GPU type unsupported by this torch, or broken)"; exit 1; }
nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader || true

# Node-local scratch, removed when the job ends however it ends.
S=/ssd_scratch/$USER/$SLURM_JOB_ID
mkdir -p "$S"
trap 'rm -rf "$S"; echo "=== job ${SLURM_JOB_ID} end $(date "+%F %T") after $(( ($(date +%s) - JOB_START) / 60 )) min"' EXIT

export OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 TOKENIZERS_PARALLELISM=false USE_TF=0 TRANSFORMERS_NO_TF=1
export HF_HOME=$PROJ/hf_cache PIP_CACHE_DIR=$S/pip TMPDIR=$S PYTHONUNBUFFERED=1
cd "$PROJ/code"
echo "=== code: $(cat VERSION 2>/dev/null || echo 'no VERSION file')"
