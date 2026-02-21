# Outlier remediation protocol (δ_total > 50%)

This repository treats **any run with δ_total > 50% in any headline observable** (M_max, R_1.4, Λ_1.4) as *high risk* for headline reporting.

## Policy (reviewer-facing)
1. **Attempt stabilization** using:
   - grid refinement `n → 2n`,
   - tighter tolerances `epsabs=epsrel=1e-12`,
   - `max_iter=400`,
   - Newton damping enabled,
   - (optionally) an alternative integrator (e.g., RK45/BDF) if available in the pipeline.
2. **Document every attempt** in `outputs/diagnostics/<run_id>/diagnosis.txt` (append-only log).
3. If stabilization fails (non-convergence or δ_total remains > 50%), **EXCLUDE** the run and index the reason in:
   - `outputs/audit_index.csv` and `outputs/audit_trail.csv`.

## Machine-readable artifacts
- Re-run plan: `outputs/rerun_plan_delta_total_gt50.csv`
- Per-run audit bundle: `outputs/diagnostics/<run_id>/`
  - `diagnosis.txt`, `run.log`, `metadata.json`, `run_config.json`, and diagnostic plots.

## How to generate / update the plan
From the repo root:
```bash
python scripts/targeted_rerun_outliers.py --runs outputs/runs_summary.csv --dry-run
```

To execute re-runs on an HPC system (requires your solver wired into `scan_wrappers.compute_tov_case`):
```bash
python scripts/targeted_rerun_outliers.py --runs outputs/runs_summary.csv --execute
```

## Snapshot note
The current repository snapshot already **EXCLUDES** known δ_total≫50% toy cases (Poly2) and provides full audit trails.
The protocol above exists so that any future δ_total>50% case is handled uniformly and transparently.
