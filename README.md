# CQG
Code + data to reproduce SFST-modified TOV neutron-star observables (M–R–Λ), with EOS/prior sensitivity and GW170817 reweighting demo
SFST/QFIS Neutron-Star Modified TOV Repository
============================================

This repository provides code, data snapshots, and scripts to reproduce the figures, tables,
and supplementary artifacts for the accompanying CQG-style manuscript. We study an EFT-motivated,
vacuum-induced inertial renormalization (SFST/QFIS, exploratory) and its impact on neutron-star
structure via modified TOV integrations.

What’s included
---------------
- FigX (3 panels): vector PDFs + 600 dpi raster exports
- Reproducibility & provenance: Git commit, Docker SHA256 digest, RNG seed, snapshot IDs
- Excluded/diagnostic run dossiers: diagnosis.txt + plots + data IDs
- Minimal GW170817-style reweighting demo (illustrative)

------------------------------------------------------------
1) Uploading to GitHub (zip vs. unzip)
------------------------------------------------------------

Unzip locally and commit the extracted files.
Do NOT upload the .zip as a single file.

Recommended workflow:
  git init
  git add .
  git commit -m "Initial import"
  git branch -M main
  git remote add origin <YOUR_GITHUB_REPO_URL>.git
  git push -u origin main

------------------------------------------------------------
2) Requirements
------------------------------------------------------------

Minimum:
- Git
- Python 3.10+ (3.11 recommended)
- make (macOS/Linux). Windows: use WSL2.

Recommended for exact reproducibility:
- Docker (recent)

------------------------------------------------------------
3) Get the code
------------------------------------------------------------

Clone:
  git clone <YOUR_GITHUB_REPO_URL>.git
  cd <REPO_FOLDER_NAME>

------------------------------------------------------------
4) Quick start (recommended): Docker
------------------------------------------------------------

This builds (or references) a Docker image, runs the canonical pipeline, generates FigX panels
(vector + 600 dpi raster), and stamps provenance (git commit, docker digest, seed) into metadata
(and into manuscript/supplement placeholders if present).

  make docker_build release DOCKER_IMAGE=sfst-qfis:local

Typical outputs:
- outputs/figX/ (FigX PDFs + 600 dpi PNGs)
- outputs/tables/
- outputs/provenance.json and outputs/provenance.txt
- figures/plot_metadata.json

Run with an exact (immutable) Docker digest:
  DOCKER_DIGEST_SHA256=sha256:<YOUR_DIGEST> make release

------------------------------------------------------------
5) Local run (no Docker): Python venv
------------------------------------------------------------

Create a venv and install requirements:
  python -m venv .venv
  source .venv/bin/activate          # macOS/Linux
  # .venv\Scripts\activate         # Windows PowerShell

  pip install -r requirements.txt

Then:
  make figX
  make provenance
  make validate_plot_metadata

------------------------------------------------------------
6) Reproduce individual artifacts
------------------------------------------------------------

6.1) FigX: three single panels (vector + 600 dpi)
  make figX

Expected files (example):
- outputs/figX/figX_panelA_convergence.pdf + .png
- outputs/figX/figX_panelB_epsratio.pdf    + .png
- outputs/figX/figX_panelC_residuals.pdf   + .png

6.2) Validate plot metadata / provenance
  make validate_plot_metadata

6.3) Build the maintext observables table
  python scripts/build_maintext_observables_table.py \
    --runs-summary outputs/runs_summary.csv \
    --out outputs/tables/maintext_observables_table.csv

6.4) EOS/Prior sanity grid (2–3 representative EOS checks)
  make sanity_table

Or directly:
  python scripts/build_eos_prior_sanity_table.py \
    --runs-summary outputs/runs_summary.csv \
    --out outputs/tables/eos_prior_sanity_grid.csv

6.5) Excluded/diagnostic run dossiers
  python scripts/generate_excluded_run_dossiers.py \
    --index supplement/excluded_runs/index.csv \
    --out supplement/excluded_runs

Each dossier includes:
- diagnosis.txt (run ID, exclusion reason, epsratio, raw output link/path)
- a diagnostic plot (png/pdf)
- data IDs (index + dossier)

6.6) Minimal GW170817-style reweighting demo
  python scripts/gw170817_reweight_demo.py \
    --in data/examples_gw/gw170817_like_posterior.csv \
    --out outputs/gw170817_reweight_demo

------------------------------------------------------------
7) Provenance stamping (placeholders -> real values)
------------------------------------------------------------

If your manuscript/supplement includes placeholders like:
  <<DOCKER_SHA256_DIGEST>>  <<GIT_COMMIT_HASH>>  <<RNG_SEED>>
the release/provenance flow replaces them automatically.

Manual stamping (if needed):
  make provenance

------------------------------------------------------------
8) Where to find submission artifacts
------------------------------------------------------------

- Figures: outputs/figX/
- Tables: outputs/tables/
- Provenance: outputs/provenance.json and outputs/provenance.txt
- Supplement provenance: supplement/*PROVENANCE*.md
- Snapshots: data/snapshots/

------------------------------------------------------------
9) Troubleshooting
------------------------------------------------------------

- No Docker: use the local venv path.
- Docker mount permissions: verify host paths and user permissions.
- Windows: use WSL2 for make and a Linux-like environment.

------------------------------------------------------------
License / Citation
------------------------------------------------------------

If you publish results based on this repository, please cite the accompanying manuscript and include
the exact Git commit and Docker digest from outputs/provenance.json.

(End of README)
