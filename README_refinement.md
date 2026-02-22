# README — automated refinement & retry for diagnostic runs

Purpose: automatically attempt stabilization of **diagnostic** runs (e.g. δ_total>50%, max_epsratio above thresholds, or solver failures) via staged grid refinement and stricter Newton tolerances. Each attempt is logged for audit.

## Key scripts
- `scripts/refine_and_retry.py` — wrapper-based local refinement using `scan_wrappers.compute_tov_case`
- `scripts/refine_and_retry_cli.py` — CLI/Slurm refinement controller (submit or run locally)
- `slurm/run_refined.sbatch` — single refinement attempt for cluster runs

## Expected artifacts
Per run attempt:
- `outputs/diagnostics/<run_tag>/summary.json`
- `outputs/diagnostics/<run_tag>/run.log` (local/CLI mode) or Slurm logs under `slurm_logs/`
Per original run:
- `outputs/diagnostics/<orig_run_id>/refinement_log.json` (append-only audit trail)

## Decision rules
- **RESOLVED**: `converged==True` and `max_epsratio <= 0.10`
- **STRESS_RESOLVED**: `converged==True` and `0.10 < max_epsratio <= 0.30`
- **UNRESOLVED**: retries exhausted; remains DIAGNOSTIC and should be **EXCLUDED** per policy

## Default refinement schedule
- `grid_factor`: [1.5, 2.0, 3.0]
- `newton_tol`:  [1e-6, 1e-7, 1e-8]
- `max_retries`: 3

## Quick start (local, wrapper mode)
```bash
python scripts/refine_and_retry.py --input outputs/audit_index.csv --n-retries 3
```

## Quick start (cluster)
Submit attempts via the CLI controller:
```bash
python scripts/refine_and_retry_cli.py --input outputs/audit_index.csv --mode slurm --n-retries 3
```
Then collect results using your existing `slurm/collect_results.sbatch` or collector script.

## Integration requirement
`scan_wrappers.compute_tov_case` must accept `extra['grid_factor']` and `extra['newton_tol']` and pass them into the solver config (e.g. `N_radial=int(N_base*grid_factor)`, `newton_tol=newton_tol`).



## Smoke-test / CI note
For lightweight smoke tests (no expensive solver), set `SFST_DUMMY=1`. The wrapper will then generate a deterministic placeholder `summary.json` and the refinement controller will still produce auditable `refinement_log.json` entries.

## Quick-start: test refinement for 5 diagnostic cases (copy/paste)

This section provides an immediately runnable local smoke test that attempts refinement on **five** diagnostic runs and collects the audit artifacts.

### 1) Create a temporary list with 5 diagnostic runs
```bash
# working directory: repo root
cd /path/to/your/repo

# Create a small audit_index containing header + 5 diagnostic/failed entries
awk -F, 'NR==1 || ($4=="DIAGNOSTIC" || $4=="FAILED" || $4=="PARSE_ERROR") {print $0}' outputs/audit_index.csv | head -n 6 > outputs/audit_index_small.csv
```
(Using `head -n 6` yields the header line plus five cases; adjust if fewer diagnostic cases exist.)

### 2) Run the local test refinement (3 retries)
```bash
python3 scripts/refine_and_retry_cli.py --input outputs/audit_index_small.csv --mode local --n_retries 3 --wait_after_submit 5
```

What happens: the script reads `outputs/audit_index_small.csv`, runs up to three attempts per `run_id` with staged `grid_factor`/`newton_tol`, creates per-attempt folders under `outputs/diagnostics/<run_tag>_ref.../`, writes `run.log` and (if your solver produces it) `summary.json`. It appends all attempts to `outputs/diagnostics/<orig_run_id>/refinement_log.json`.

### 3) Sanity-check created attempts
```bash
ls -1 outputs/diagnostics | sed -n '1,20p'
jq . outputs/diagnostics/<RUN_ID>/refinement_log.json
```
Replace `<RUN_ID>` by an actual original run directory name.

### 4) Expected fields in summary.json
`summary.json` should contain at least:
```json
{
  "run_id": "SLy_abc123_ref1_gf1.5_nt1e-6",
  "eos": "SLy",
  "sigma": 1.23e-4,
  "converged": true,
  "M_max": 2.01,
  "R_1p4": 11.8,
  "Lambda_1p4": 350,
  "max_epsratio": 0.085,
  "wfaktor_max": 1234.5,
  "newton_final_residual": 1e-8
}
```
If `summary.json` is missing, inspect `run.log` and `diagnosis.txt` in the same folder.

### 5) Interpreting outcomes (as logged)
- **RESOLVED**: `converged==true` and `max_epsratio ≤ 0.10`
- **STRESS_RESOLVED**: `converged==true` and `0.10 < max_epsratio ≤ 0.30`
- **UNRESOLVED**: no convergence or `max_epsratio > 0.30` after all retries

These statuses appear as entries in `outputs/diagnostics/<orig_run_id>/refinement_log.json`.

### 6) Update audit and scan indices
After the test runs, update `outputs/audit_index.csv` / `outputs/scan_grid.csv` using your collector script, e.g.
```bash
python3 scripts/collect_results.py --input outputs/diagnostics --audit outputs/audit_index.csv
```
If you do not have a collector yet, parse the new `summary.json` files and append/update the relevant rows manually (or add a small helper script).

### 7) Example refinement_log.json entry
```json
[
  {
    "timestamp": "2026-02-17T21:00:00Z",
    "status": "ATTEMPT_RESULT",
    "attempt": 1,
    "grid_factor": 1.5,
    "newton_tol": 1e-6,
    "run_tag": "SLy_abc123_ref1_gf1.5_nt1e-6",
    "converged": false,
    "max_epsratio": 0.45
  },
  {
    "timestamp": "2026-02-17T21:30:00Z",
    "status": "UNRESOLVED",
    "note": "exhausted retries; remains diagnostic"
  }
]
```

### 8) Optional: Slurm/cluster mode
Adjust `run_refined.sbatch` (`WORKDIR`, partition, python path). Build a run list:
```bash
awk -F, 'NR>1 && ($4=="DIAGNOSTIC" || $4=="FAILED" || $4=="PARSE_ERROR") {print $1}' outputs/audit_index.csv > refine_runlist.txt
```
Submit serially (or convert to an array job):
```bash
while read -r RUNID; do
  sbatch run_refined.sbatch "${RUNID}" 2.0 1e-7
done < refine_runlist.txt
```


## Quickstart (5 diagnostic cases, local test)
From the repository root:

```bash
# create a small audit list containing header + first 5 diagnostic rows
awk -F, 'NR==1 || ($4=="DIAGNOSTIC" || $4=="FAILED" || $4=="PARSE_ERROR") {print $0}' outputs/audit_index.csv | head -n 6 > outputs/audit_index_small.csv

# run staged refinement (3 retries)
python3 scripts/refine_and_retry_cli.py --input outputs/audit_index_small.csv --mode local --n_retries 3 --wait_after_submit 5

# collect summary.json files and update outputs/scan_grid.csv + outputs/audit_index.csv
python3 scripts/collect_results.py
```

Artifacts of each attempt are written to `outputs/diagnostics/<run_tag>/` (including `run.log`, `summary.json` if produced), and the per-original-run `refinement_log.json` is appended under `outputs/diagnostics/<orig_run_id>/refinement_log.json`.
