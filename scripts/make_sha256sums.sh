#!/usr/bin/env bash
set -euo pipefail

# Generate SHA256 checksums for release archives.
# Usage: bash scripts/make_sha256sums.sh

cd "$(git rev-parse --show-toplevel)"

: "${ZIP:=sfst-qfis-release.zip}"
: "${TAR:=sfst-qfis-release.tar.gz}"

if [ -f "$ZIP" ]; then
  sha256sum "$ZIP" > "$ZIP.sha256"
  echo "Wrote $ZIP.sha256"
fi

if [ -f "$TAR" ]; then
  sha256sum "$TAR" > "$TAR.sha256"
  echo "Wrote $TAR.sha256"
fi

# Optional aggregate file
{
  [ -f "$ZIP.sha256" ] && cat "$ZIP.sha256"
  [ -f "$TAR.sha256" ] && cat "$TAR.sha256"
} > SHA256SUMS.txt || true

echo "Wrote SHA256SUMS.txt"
