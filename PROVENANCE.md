# Provenance
We use this file to pin the numerical environment so reviewers can reproduce results (or understand controlled drift).

## Container and library versions
- Docker image: recorded by digest in `outputs/provenance.txt` (created by `scripts/print_provenance.sh`)
- Python version: recorded in `outputs/provenance.txt`
- pip packages: recorded in `outputs/provenance.txt` (pip freeze)
- BLAS/MKL/OpenBLAS: recorded in `outputs/provenance.txt` where available
- CI runner image: recorded in CI logs (ubuntu-latest)

## Determinism controls
In Docker and CI we force single-threaded math libraries:
- OMP_NUM_THREADS=1
- MKL_NUM_THREADS=1
- OPENBLAS_NUM_THREADS=1
- NUMEXPR_NUM_THREADS=1

## Seeds
We centralize RNG seeds in `config/seeds.yaml` and we load them from there in scripts that use randomness. we also include `scripts/check_seeds.py` as a guard.

## Hashes
See `SHA256SUMS.txt` for archive and artefact hashes.

## Figure X numerical validation (added)
- Plot script: `scripts/plot_figureX.py`
- Example I/O schemas: `data/examples/` (convergence.csv, epsratio_summary.csv, residual_traces.h5)
- Metadata template: `plot_metadata.json.template` (generated at runtime as `figures/plot_metadata.json`)
- Provenance/specification details: `supplement/SUPPLEMENT_FIGX_PROVENANCE.md`
