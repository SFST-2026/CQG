#!/usr/bin/env bash
set -euo pipefail

# Run refinement retries for the most important diagnostic cases.
# Criteria:
#  - status in {DIAGNOSTIC,FAILED,PARSE_ERROR} OR
#  - delta_total_percent > 50 (if that column exists in audit_index.csv)

AUDIT=${1:-outputs/audit_index.csv}
N=${2:-10}
OUT_SMALL=outputs/audit_index_small_top${N}.csv

mkdir -p outputs

if [ ! -f "$AUDIT" ]; then
  echo "ERROR: $AUDIT not found" >&2
  exit 2
fi

# Prefer delta_total_percent filter if present; otherwise fall back to status filter.
HEADER=$(head -n 1 "$AUDIT")
if echo "$HEADER" | grep -qi "delta_total"; then
  # keep header + top N rows with delta_total > 50 (numeric), else status-based
  awk -F, 'NR==1{print; next} {for(i=1;i<=NF;i++) if(tolower($i)~"delta_total") dt=i} {if(dt>0 && $dt+0>50) print}' "$AUDIT" | head -n $((N+1)) > "$OUT_SMALL" || true
fi

# If OUT_SMALL only has header (or missing), use status filter:
if [ ! -s "$OUT_SMALL" ] || [ "$(wc -l < "$OUT_SMALL")" -le 1 ]; then
  awk -F, 'NR==1 || ($4=="DIAGNOSTIC" || $4=="FAILED" || $4=="PARSE_ERROR") {print}' "$AUDIT" | head -n $((N+1)) > "$OUT_SMALL"
fi

echo "Wrote $OUT_SMALL"
python3 scripts/refine_and_retry_cli.py --input "$OUT_SMALL" --mode local --n_retries 3 --wait_after_submit 5
python3 scripts/collect_results.py
mv outputs/audit_index_updated.csv outputs/audit_index.csv
echo "Updated outputs/audit_index.csv"
