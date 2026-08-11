#!/bin/bash
#SBATCH --job-name=flan-t5
#SBATCH --output=logs/%x.%j.out
#SBATCH --error=logs/%x.%j.err
#SBATCH --mail-user=islams32@myumanitoba.ca
#SBATCH --mail-type=BEGIN,END,FAIL
#SBATCH --time=6:00:00
#SBATCH --gres=gpu:h100:2
#SBATCH --cpus-per-task=1
#SBATCH --mem=120G
mkdir -p logs
set -euo pipefail
echo "Job started on $(hostname) at $(date)"
module load python
module load scipy-stack
module load ipykernel
module load StdEnv
module load cuda
module load arrow
cd /home/shahidul/projects/def-shaiful/shahidul/technical-debt/satd-core
source /home/shahidul/projects/def-shaiful/shahidul/technical-debt/.venv/bin/activate
export HF_HOME=$SLURM_TMPDIR/hf_cache
mkdir -p $HF_HOME
MODEL_NAME=${1:-"google/flan-t5-small"}
SHOT=${2:-"0"}
PROMPT_NAME=${3:-"default"}
DATASET_NAME=${4:-"unique"}
RUN_INDEX=${5:-"1"}

srun python detect-flan-t5.py \
    --prompt-name "$PROMPT_NAME" \
    --model-name "$MODEL_NAME" \
    --dataset-name "$DATASET_NAME" \
    --shot "$SHOT" \
    --run-index "$RUN_INDEX"
echo "Job finished at $(date)"
