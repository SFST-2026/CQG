#!/usr/bin/env bash
set -euo pipefail

OUT="${1:-outputs/provenance.txt}"
mkdir -p "$(dirname "$OUT")"

{
  echo "date: $(date -u +"%Y-%m-%dT%H:%M:%SZ")"
  echo "python: $(python -V 2>&1 || true)"
  echo "pip: $(pip -V 2>&1 || true)"
  echo "uname: $(uname -a || true)"
  echo "env: OMP_NUM_THREADS=${OMP_NUM_THREADS:-} MKL_NUM_THREADS=${MKL_NUM_THREADS:-} OPENBLAS_NUM_THREADS=${OPENBLAS_NUM_THREADS:-} NUMEXPR_NUM_THREADS=${NUMEXPR_NUM_THREADS:-}"
  echo "pip_freeze:"
  pip freeze 2>/dev/null || true
  echo "blas_info:"
  python - <<'PY' 2>/dev/null || true
import numpy as np
try:
    np.__config__.show()
except Exception as e:
    print("numpy config unavailable:", e)
PY
} > "$OUT"

echo "[provenance] wrote $OUT"
