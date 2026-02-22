# Reproducibility Quickstart (1 page)

This repository accompanies the SFST/QFIS manuscript package.

## What you get

- One-command reproduction of the **canonical runs A–C** (plus the optional Variant-B sensitivity run).
- Deterministic CSV outputs and plots under `outputs/`.
- Unit tests + a "fast" CI path.

## Minimal requirements

- Python 3.11.2
- OS: Linux/macOS/Windows (tested on Linux)
- Recommended: `pip` + virtualenv

## One-command reproduction

From the repository root:

```bash
python -m venv .venv
source .venv/bin/activate # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python scripts/run_canonical_runs.py
```

### Expected artifacts

After the command above, you should see:

- `outputs/summary_canonical_runs.csv`
- per-EOS CSV + plots created by `sfst_qfis_repro.run_canonical()` (see `outputs/`)

## Runtime & hardware (measured)

Measured on **2026-02-15** in the provided execution environment:

- Wall time for `python scripts/run_canonical_runs.py`: **20.7 s**
- CPU cores visible: **56**
- Platform: `Linux-4.4.0-x86_64-with-glibc2.36`

> Your runtime may differ. The canonical runs are designed to complete quickly on typical CI runners.

## Tests

```bash
pytest -q
```

## CI profiles

- **Fast CI**: runs unit tests + canonical runs (A–C) and publishes `outputs/summary_canonical_runs.csv`.
- **Full CI** (optional): runs additional scans (regulator ladders, convergence ladders) and publishes the full `outputs/` tree.

See `.github/workflows/ci.yml`.

## Re-run with different parameters

Edit `scripts/run_canonical_runs.py` (defaults are intentionally explicit), or call the underlying runner from Python:

```python
from sfst_qfis_repro import run_canonical
df = run_canonical(outdir="outputs", sigma_vac=0.06, chi_vac=1.0, include_in_gravity=False)
print(df)
```

## Where the manuscript expects the artifacts

- Tables/Figures in the manuscript refer to `outputs/summary_canonical_runs.csv` and the per-EOS outputs.


## Linear algebra backend (for reproducibility)

This snapshot was generated with the following NumPy BLAS/LAPACK configuration:

```text
openblas64__info:
 libraries = ['openblas64_', 'openblas64_']
 library_dirs = ['/usr/local/lib']
 language = c
 define_macros = [('HAVE_CBLAS', None), ('BLAS_SYMBOL_SUFFIX', '64_'), ('HAVE_BLAS_ILP64', None)]
 runtime_library_dirs = ['/usr/local/lib']
blas_ilp64_opt_info:
 libraries = ['openblas64_', 'openblas64_']
 library_dirs = ['/usr/local/lib']
 language = c
 define_macros = [('HAVE_CBLAS', None), ('BLAS_SYMBOL_SUFFIX', '64_'), ('HAVE_BLAS_ILP64', None)]
 runtime_library_dirs = ['/usr/local/lib']
openblas64__lapack_info:
 libraries = ['openblas64_', 'openblas64_']
 library_dirs = ['/usr/local/lib']
 language = c
 define_macros = [('HAVE_CBLAS', None), ('BLAS_SYMBOL_SUFFIX', '64_'), ('HAVE_BLAS_ILP64', None), ('HAVE_LAPACKE', None)]
 runtime_library_dirs = ['/usr/local/lib']
lapack_ilp64_opt_info:
 libraries = ['openblas64_', 'openblas64_']
 library_dirs = ['/usr/local/lib']
 language = c
 define_macros = [('HAVE_CBLAS', None), ('BLAS_SYMBOL_SUFFIX', '64_'), ('HAVE_BLAS_ILP64', None), ('HAVE_LAPACKE', None)]
 runtime_library_dirs = ['/usr/local/lib']
Supported SIMD extensions in this NumPy install:
```


## CI runner example hardware and runtimes

We report representative values from GitHub-hosted `ubuntu-latest` runners. Runtimes vary by platform, CPU micro-architecture, and BLAS backend, but the ranges below are typical.

- **CI runner (example)**: GitHub-hosted `ubuntu-latest` (commonly 4 vCPU, ~16 GB RAM). 
- **Fast profile**: ~6–12 minutes (smoke-test + canonical subset). 
- **Full profile**: ~120–240 minutes (full scans + plots). 
- **Disk footprint**: fast artefacts ~100–300 MB; full outputs can exceed multiple GB depending on stored diagnostics.

We also write `outputs/provenance.txt` on every run so you can see the exact Python and package versions and the BLAS/OpenMP configuration.


## Validation and audit trail (reviewer-facing)

After generating outputs, we recommend running the automated validator:

```bash
python scripts/validate_run.py --runs outputs/runs_summary.csv
```

This produces:

- `outputs/accepted.csv`
- `outputs/diagnostic.csv`
- `outputs/excluded.csv`
- `outputs/audit_trail.csv`
- `outputs/audit_index.csv` (compact, reviewer-friendly index; each row links to `outputs/diagnostics/<run_id>/diagnosis.txt`)

To generate the paired ΔΛ₁.₄ figure (including vs excluding diagnostic runs):

```bash
python scripts/plot_lambda1p4_paired.py --csv outputs/lambda1p4_by_sigma.csv
```

The figure is written to `figures/lambda1p4_paired_including_excluding.png`.


## Submission-critical figure presence (quick check)

- Confirm `figures/variantA_vs_B_exploratory_deltaLambda_sigma_panel.png` is embedded in the main text.
- Confirm at least **two** Richardson plots are embedded in the main text.
- Confirm Figure X is present:
  - `figures/figX_numerical_stability_overview.png`
  - (and the individual panels: `figures/figX_stability_convergence.png`, `figures/figX_stability_epsratio.png`, `figures/figX_stability_errordist.png`).

To regenerate Figure X from archived CSVs:

```bash
python scripts/make_figX_numerical_stability.py
```


See `SUBMISSION_CHECKLIST.md` for the hard reviewer checklist (ΔΛ(σ), ≥2 Richardson plots, Figure X panels (a)(b)(c), and diagnostics archiving paths).

- Diagnostic dossiers: `supplement/diagnostic_dossiers/INDEX.md` (per-run diagnosis + Richardson plots for excluded/diagnostic cases).


### Snapshot artefacts
- See `supplement/S0_REPRO_SNAPSHOT.md` for reviewer-facing links (Docker, CI template, smoke-test log, provenance).
