# Release / public archive checklist (Git tag + Zenodo DOI)

This file is copy‑paste ready. It produces a public, auditable archive for submission: a **Git tag**, a **Zenodo DOI**, and a verifiable **SHA256SUMS** manifest.

> Notes
> - Replace placeholders like `<GITHUB_REMOTE>` or `<ZENODO_RECORD_URL>`.
> - If you use a private mirror, tag there first, then push the tag to the public mirror.
> - Zenodo DOI generation requires manual steps in the Zenodo UI.

---

## 0) Preconditions (one‑time)
1) Ensure the repository is clean:
```bash
git status
```

2) Ensure you can build/run the minimal checks:
```bash
python scripts/validate_run.py --runs outputs/runs_summary.csv
```

3) Ensure the headline outputs exist (and match what the manuscript cites):
```bash
ls -lah outputs/headline_with_diagnostics.csv outputs/headline_without_diagnostics.csv
```

---

## 1) Freeze the exact submission state
### 1.1 Update version identifiers
Decide a tag name, e.g.:
- `v1.0.0-submission`
- `v1.0.1-submission` (if you already tagged once)

Set it:
```bash
export TAG="v1.0.0-submission"
```

### 1.2 Generate / refresh SHA256SUMS
Generate checksums (Linux/macOS with coreutils `sha256sum`):
```bash
# From repo root
find . -type f \
  -not -path "./.git/*" \
  -not -path "./.venv/*" \
  -not -path "./venv/*" \
  -not -path "./__pycache__/*" \
  -not -name "*.pyc" \
  -print0 | sort -z | xargs -0 sha256sum > SHA256SUMS.txt
```

Spot check:
```bash
head -n 5 SHA256SUMS.txt
wc -l SHA256SUMS.txt
```

### 1.3 Commit the checksum manifest
```bash
git add SHA256SUMS.txt
git commit -m "Archive: add SHA256SUMS for ${TAG}"
```

---

## 2) Create and push the Git tag
Create an annotated tag:
```bash
git tag -a "${TAG}" -m "Submission archive ${TAG}"
```

Push commit + tag to your remote:
```bash
# Replace origin if needed
git push origin main
git push origin "${TAG}"
```

Verify tag is present:
```bash
git show "${TAG}" --no-patch
```

---

## 3) Create the Zenodo archive (DOI)
### Option A — GitHub→Zenodo integration (recommended)
1) In Zenodo: connect your GitHub account and enable the repository.
2) Trigger a new release **from the Git tag** (GitHub Releases UI).
3) Zenodo will ingest the release and mint a DOI.
4) Record:
   - **Concept DOI** (stable across versions)
   - **Version DOI** (specific to this release)

Store the DOI(s) in your manuscript’s Data & Code Availability section.

### Option B — Manual upload (zip)
1) Create a release zip from the tag:
```bash
git archive --format=zip --output "sfst-qfis-${TAG}.zip" "${TAG}"
```
2) Upload to Zenodo and publish.
3) Copy the minted DOI.

---

## 4) Update Data & Code Availability (manuscript)
Update the Data & Code Availability paragraph to include:
- Repository URL (or “available at DOI archive”)
- **Zenodo version DOI**
- Git tag name `${TAG}`
- SHA256SUMS mention

Copy‑paste template:

**Data & Code Availability.** The code and data supporting this work are archived under a citable Zenodo record (version DOI: **<ZENODO_VERSION_DOI>**; concept DOI: **<ZENODO_CONCEPT_DOI>**). The archive corresponds to Git tag **${TAG}** and includes a checksum manifest (**SHA256SUMS.txt**) for integrity verification. Headline machine‑readable outputs are provided as `outputs/headline_with_diagnostics.csv` and `outputs/headline_without_diagnostics.csv`, and the audit trail for diagnostic/excluded runs is indexed in `outputs/audit_index.csv`.

---

## 5) Recommended Zenodo upload contents (reviewer-friendly)
Include at minimum:
- `outputs/headline_with_diagnostics.csv`
- `outputs/headline_without_diagnostics.csv`
- `outputs/audit_index.csv` and `outputs/audit_trail.csv`
- `outputs/diagnostics/` (or at least diagnostics for excluded runs)
- `figures/` used in the paper
- `scripts/` and `docs/`
- `SHA256SUMS.txt`

---

## 6) Verify the archive matches the tag
After Zenodo publish:
1) Download the Zenodo zip and verify checksums:
```bash
# In a fresh directory
sha256sum -c SHA256SUMS.txt | head
```

2) Record the Zenodo record URL for your supplement:
- `<ZENODO_RECORD_URL>`

---

## 7) Final “submission-ready” sanity checks
- Variant‑B gate is stated in Methods and Appendix A.7 (Variant B exploratory unless independent `c_src` matching).
- All δ_total>50% cases have either:
  - a resolved refinement trail (`refinement_log.json` showing RESOLVED/STRESS_RESOLVED), or
  - an explicit exclusion + audit entry.
- The one-page reviewer checklist exists: `docs/REVIEWER_RISK_CLOSURE_ONEPAGE.md`
- Refinement protocol exists: `README_refinement.md`

