#!/bin/bash
#SBATCH --job-name=sfst_scan
#SBATCH --output=slurm_logs/array_%A_%a.out
#SBATCH --error=slurm_logs/array_%A_%a.err
#SBATCH --time=04:00:00
#SBATCH --mem=12G
#SBATCH --cpus-per-task=1
#SBATCH --array=1-100%40
#SBATCH --partition=standard

set -euo pipefail

# ====== EDIT THESE PATHS ======
WORKDIR=/home/youruser/projects/sfst_repo        # <-- set to your repo path
PARAMS=${WORKDIR}/params.csv
OUTPUT_BASE=${WORKDIR}/outputs/diagnostics
LOGDIR=${WORKDIR}/slurm_logs
VENV_ACTIVATE=${WORKDIR}/venv/bin/activate      # optional; leave empty if unused
SINGIMG=                                         # optional: /path/to/container.sif
# ==============================

mkdir -p "${OUTPUT_BASE}" "${LOGDIR}"

TASK_ID=${SLURM_ARRAY_TASK_ID}
LINE=$(sed -n "$((TASK_ID+1))p" "${PARAMS}" || true)
if [ -z "${LINE}" ]; then
  echo "No parameter line for TASK_ID=${TASK_ID}" >&2
  exit 2
fi
IFS=',' read -r EOS G GAMMA SEED <<< "${LINE}"

export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1
export SFST_SEED=${SEED}

TIMESTAMP=$(date -u +"%Y%m%dT%H%M%SZ")
RUN_TAG="${EOS}_g${G}_G${GAMMA}_${TIMESTAMP}_${SLURM_ARRAY_JOB_ID}_${SLURM_ARRAY_TASK_ID}"
RUN_DIR="${OUTPUT_BASE}/${RUN_TAG}"
mkdir -p "${RUN_DIR}"

cat > "${RUN_DIR}/meta.txt" <<EOF
run_tag: ${RUN_TAG}
eos: ${EOS}
g: ${G}
Gamma: ${GAMMA}
seed: ${SEED}
slurm_job: ${SLURM_ARRAY_JOB_ID}
slurm_task: ${SLURM_ARRAY_TASK_ID}
timestamp: ${TIMESTAMP}
EOF

cd "${WORKDIR}"

if [ -n "${VENV_ACTIVATE}" ] && [ -f "${VENV_ACTIVATE}" ]; then
  # shellcheck disable=SC1090
  source "${VENV_ACTIVATE}"
fi

PYCODE="from scan_wrappers import compute_tov_case; res = compute_tov_case(eos='${EOS}', sigma=float(${G}**2)/float(${GAMMA}), run_tag='${RUN_TAG}', extra={'g':${G},'Gamma':${GAMMA},'seed':${SEED}}); import json, pathlib; pathlib.Path('${RUN_DIR}/summary.json').write_text(json.dumps(res)); print('Done')"

if [ -n "${SINGIMG}" ] && [ -f "${SINGIMG}" ]; then
  singularity exec --bind "${WORKDIR}:${WORKDIR}" "${SINGIMG}" python -u -c "${PYCODE}"
else
  python -u -c "${PYCODE}"
fi

if [ ! -f "${RUN_DIR}/summary.json" ]; then
  echo "ERROR: summary.json missing for ${RUN_TAG}" >&2
  echo "marking as failed" > "${RUN_DIR}/diagnosis.txt"
  exit 3
fi

echo "Task ${SLURM_ARRAY_TASK_ID} finished successfully"
