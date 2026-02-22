# Packaging generated artifacts for readers download (English, copy/paste)

This repository produces figures/tables/logs/scripts that are helpful for readers. The steps below collect them into a single archive, generate checksums, and optionally publish the archive via a GitHub Release and/or Zenodo.

## Quick option: one-command packaging

```bash
bash scripts/package_release_artifacts.sh
```
This produces the release archives and SHA256 checksums in the repo root.

## 1) Collect files and create ZIP/TAR (local)
```bash
# Working directory: repo root
cd /path/to/your/repo

# Create a staging folder for the release bundle
mkdir -p release_artifacts

# Copy expected artifacts (adjust paths if your repo differs)
cp -r outputs/figures release_artifacts/figures || true
cp -r outputs/tables  release_artifacts/tables  || true
cp -r outputs/texts   release_artifacts/texts   || true
cp -r outputs/logs    release_artifacts/logs    || true
cp -r scripts         release_artifacts/scripts || true

# Optional: add a short README describing contents
cat > release_artifacts/README.txt <<'EOF'
Repository snapshot for readers download.
Included:
- figures/deltaLambda_sigma_SLy_AP4.png
- figures/richardson_SLy.png
- figures/richardson_AP4.png
- figures/richardson_Poly2toy.png
- tables/comparison_table_SLy_AP4.csv
- texts/figure_caption_deltaLambda.txt
- logs/generation_log.txt
- scripts/refine_and_retry_cli.py (if present)
EOF

# Create archives
zip -r sfst-qfis-release.zip release_artifacts
tar -czf sfst-qfis-release.tar.gz release_artifacts
```

## 2) Generate SHA256 checksums
```bash
sha256sum sfst-qfis-release.zip > sfst-qfis-release.zip.sha256
sha256sum sfst-qfis-release.tar.gz > sfst-qfis-release.tar.gz.sha256
```

## 3) Optional: temporary local HTTP download (short-lived)
```bash
python3 -m http.server 8000
# Download: http://<your-host>:8000/sfst-qfis-release.zip
```
(Use only for short internal sharing; consider firewall/network implications.)

## 4) GitHub Release (recommended) + tag
```bash
git add -A
git commit -m "Release: submission snapshot"
git tag -a v1.0.0-submission -m "submission snapshot v1.0.0-submission"
git push origin main
git push origin v1.0.0-submission

# Attach archives with GitHub CLI (gh)
gh release create v1.0.0-submission sfst-qfis-release.zip sfst-qfis-release.tar.gz   --title "sfst-qfis submission snapshot v1.0.0-submission"   --notes "Includes figures, tables, logs, scripts and SHA256 checksums."
```

## 5) Zenodo upload (manual)
1. Log into Zenodo.
2. Create a new upload and attach `sfst-qfis-release.zip`.
3. Fill metadata (title, authors, description, license).
4. Zenodo mints a DOI. Add it to the manuscript’s Data & Code Availability section.

## 6) Minimal readers email workflow
- Provide the GitHub Release URL or the Zenodo DOI.
- Include the SHA256 line from `sfst-qfis-release.zip.sha256`.
- Verification:
```bash
sha256sum -c sfst-qfis-release.zip.sha256
```

## 7) Checklist: what goes into the archive
- `figures/` — PNG/PDF (ΔΛ, Richardson plots)
- `tables/` — CSV comparison tables
- `texts/` — captions/README snippets
- `logs/` — generation logs and `refinement_log.json` (audit)
- `scripts/` — refinement + collection scripts
- `SHA256SUMS.txt` — aggregated checksums (optional)
