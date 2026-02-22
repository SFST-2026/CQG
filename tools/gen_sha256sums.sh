#!/usr/bin/env bash
set -euo pipefail
FILES=(
  manuscript.docx
  Dockerfile
  requirements.txt
  README.md
  REPRO_CHECKLIST.md
  SUBMISSION_CHECKLIST.md
)
# Add outputs if present
if [ -d outputs ]; then
  while IFS= read -r -d '' f; do FILES+=("$f"); done < <(find outputs -maxdepth 2 -type f -print0)
fi
sha256sum "${FILES[@]}" > SHA256SUMS.txt
echo "Wrote SHA256SUMS.txt with ${#FILES[@]} entries."
