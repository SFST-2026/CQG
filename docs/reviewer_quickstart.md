# readers Quickstart (fast validation)

We provide a self-contained repository snapshot and all numerical outputs used for my tables and figures as supplementary archives. This page gives the minimal steps to validate the snapshot.

## Option A: Docker (recommended)
```bash
docker build -t sfst-qfis:review .
docker run --rm -v "$PWD/outputs:/work/outputs" sfst-qfis:review reproduce --profile fast
./scripts/smoke_test.sh
```

## Option B: Local Python (no Docker)
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
SFST_QFIS_FAST=1 python scripts/run_all.py
./scripts/smoke_test.sh
```

## What should appear
- `outputs/summary_canonical_runs.csv`
- `outputs/uncertainty_budget_components.csv`
- `outputs/provenance.txt`
- `outputs/wfaktor_summary.csv` (if I enable wfaktor batch in the run)

## Canonical checks (fast profile)
My smoke test checks a small number of values within tolerances (and fails CI if they drift):
- `Mmax_SLy` in `[2.05, 2.10]`
- `R1p4_SLy_km` in `[8.4, 9.3]`
- `Lambda1p4_SLy` is finite and positive

If your platform differs (CPU/BLAS), I expect tiny last-digit drift; the tolerances in `scripts/smoke_test.sh` are designed to absorb this while still catching regressions.


See also: docs/REFINEMENT_TEST_QUICKSTART.md for a 5-case local refinement test.


## Additional appendix material
- CDF-II W-boson mass shift (error propagation + systematic breakdown): `docs/Appendix_Wmass_error.tex` *(speculative comparison; not evidence of causal explanation)*