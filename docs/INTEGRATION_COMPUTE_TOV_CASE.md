# compute_tov_case wrapper template and HPC integration guide

This repository includes a **template wrapper** `compute_tov_case(...)` in `scan_wrappers.py`.
It is designed to bridge the (g, Γ) scan driver (`scripts/scan_mapping_sigma_g2_over_Gamma.py`)
to your existing TOV pipeline while enforcing **deterministic runs** and **auditable per-run artifacts**.

## File/dir conventions

- Per-run artifacts:
  - `outputs/diagnostics/<run_id>/`
    - `metadata.json`, `run_config.json`
    - `summary.json` *(required; written by your pipeline)*
    - `run.log` *(recommended)*
    - `richardson.png`, `residuals.png`, `wfaktor.png` *(optional but recommended)*
    - `diagnosis.txt/json` *(on failure)*
- Master scan table:
  - `outputs/scan_grid.csv`

## Determinism

Before each run, set:
- `OMP_NUM_THREADS=1`, `MKL_NUM_THREADS=1`, `OPENBLAS_NUM_THREADS=1`, `NUMEXPR_NUM_THREADS=1`
- `SFST_SEED=<seed>` (or your project’s RNG seed convention)

## Required output contract (summary.json)

Your pipeline should write `summary.json` into the run directory with at least:

- `M_max`, `R_1p4`, `Lambda_1p4`
- `max_epsratio`, `wfaktor_max`, `newton_final_residual`
- `converged` (bool)

The wrapper will read these fields and return the standardized dict expected by the scan scripts.

## Where to connect your pipeline

Edit **one function** in `scan_wrappers.py`:

- `_call_tov_entrypoint(config_path, run_dir, env, timeout)`

Replace the placeholder with a call to your CLI / Python entrypoint (e.g., `subprocess.run([...])`)
that produces `summary.json` and diagnostics inside `run_dir`.

## Validation hook (recommended)

After each run completes you may call the existing validator to classify ACCEPTED/STRESS/DIAGNOSTIC,
and store this classification in `run_index.json`:

- `python scripts/validate_run.py --run-dir outputs/diagnostics/<run_id>`

(Adjust flag names to your validator’s interface.)

## Slurm templates

For cluster execution we provide copy-paste templates in `slurm/`:

- `slurm/run_array.sbatch` – array job over a CSV parameter file `params.csv`
- `slurm/collect_results.sbatch` – collection job that builds `outputs/scan_grid.csv`
  and a lightweight `outputs/audit_index.csv`

See the comments at the top of each file for the few paths you need to adjust.


## Smoke test (no real numerics)

For an end-to-end plumbing check without wiring your solver yet, run:

```bash
SFST_DRYRUN=1 make scan_gGamma_small
```

This generates synthetic `summary.json` files under `outputs/diagnostics/<run_id>/` and writes `outputs/scan_mapping_small/scan_grid.csv`.
