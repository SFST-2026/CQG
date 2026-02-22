#!/bin/bash
#SBATCH --job-name=sfst_refine
#SBATCH --output=slurm_logs/refine_%j.out
#SBATCH --time=02:00:00
#SBATCH --mem=12G
#SBATCH --cpus-per-task=1
#SBATCH --partition=standard

set -euo pipefail

# Usage:
#   sbatch slurm/run_refined.sbatch <EOS> <SIGMA> <ORIG_RUN_ID> <GRID_FACTOR> <NEWTON_TOL>

EOS="$1"
SIGMA="$2"
ORIG_RUN_ID="$3"
GRID_FACTOR="$4"
NEWTON_TOL="$5"

WORKDIR="$(pwd)"
mkdir -p slurm_logs outputs/diagnostics

export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1

TIMESTAMP=$(date -u +"%Y%m%dT%H%M%SZ")
RUN_TAG="${ORIG_RUN_ID}_ref_${TIMESTAMP}_gf${GRID_FACTOR}_nt${NEWTON_TOL}"
RUN_DIR="outputs/diagnostics/${RUN_TAG}"
mkdir -p "${RUN_DIR}"

python -u -c "from scan_wrappers import compute_tov_case; res = compute_tov_case(eos='${EOS}', sigma=float('${SIGMA}'), run_tag='${RUN_TAG}', extra={'grid_factor':float('${GRID_FACTOR}'),'newton_tol':float('${NEWTON_TOL}')}); import json, pathlib; pathlib.Path('${RUN_DIR}/summary.json').write_text(json.dumps(res)); print('Done')"
