#!/usr/bin/env bash
set -euo pipefail

# Package artifacts into a reviewer-friendly bundle + checksums.
# Usage:
#   bash scripts/package_release_artifacts.sh
#
# Outputs (repo root):
#   - sfst-qfis-release.zip
#   - sfst-qfis-release.tar.gz
#   - sfst-qfis-release.zip.sha256
#   - sfst-qfis-release.tar.gz.sha256

cd "$(git rev-parse --show-toplevel)"

mkdir -p release_artifacts
rm -rf release_artifacts/*

# Collect expected artifacts (best-effort; missing folders are OK)
cp -r outputs/figures release_artifacts/figures 2>/dev/null || true
cp -r outputs/tables  release_artifacts/tables  2>/dev/null || true
cp -r outputs/texts   release_artifacts/texts   2>/dev/null || true
cp -r outputs/logs    release_artifacts/logs    2>/dev/null || true
cp -r outputs/diagnostics release_artifacts/diagnostics 2>/dev/null || true
cp -r scripts         release_artifacts/scripts 2>/dev/null || true
cp -r docs            release_artifacts/docs    2>/dev/null || true

cat > release_artifacts/README.txt <<'EOF'
Repository snapshot for reviewer download.

Included (if present):
- figures/ (ΔΛ vs σ panels, Richardson plots, paired figures)
- tables/  (headline and comparison CSVs)
- texts/   (captions, notes)
- diagnostics/ (per-run summaries + refinement_log.json audit trail)
- logs/    (generation logs)
- scripts/ and docs/

See docs/release_packaging.md for GitHub Release / Zenodo DOI steps.
EOF

# Create archives
rm -f sfst-qfis-release.zip sfst-qfis-release.tar.gz
zip -r sfst-qfis-release.zip release_artifacts >/dev/null
tar -czf sfst-qfis-release.tar.gz release_artifacts

# Checksums
sha256sum sfst-qfis-release.zip > sfst-qfis-release.zip.sha256
sha256sum sfst-qfis-release.tar.gz > sfst-qfis-release.tar.gz.sha256

echo "Created:"
echo " - sfst-qfis-release.zip"
echo " - sfst-qfis-release.zip.sha256"
echo " - sfst-qfis-release.tar.gz"
echo " - sfst-qfis-release.tar.gz.sha256"
