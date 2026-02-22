# Excluded / Diagnostic Runs — Index

This directory provides a transparent audit trail for runs that were **excluded** from headline figures or retained only as **diagnostic/stress-test** cases.

## Inclusion / exclusion logic (summary)

- **Accepted (headline):** runs satisfying all basic diagnostics and **perturbative control** gate (nominally `max_r |epsratio(r)| ≤ 0.10`).
- **Diagnostic / stress-test:** runs that pass solver health checks but exceed the nominal perturbative gate (typically `0.10 < max_r|epsratio| ≤ 0.30`) or probe alternative settings.
- **Excluded:** runs that fail solver health checks (non-convergence, constraint violations, invalid profiles) or exceed stress-test thresholds.

## Index table

The machine-readable index is:

- `index.csv` (columns: `run_id`, `status`, `reason_code`, `reason_detail`, `data_ids`, `dossier_path`)

The `data_ids` column points to the primary artefacts (run outputs/logs) that support each decision.

## Per-run dossiers

Each run has a dossier directory:

- `diagnosis.txt` — concise reason + key metrics
- `residual_trace.png` — solver residual vs iteration
- `epsratio_profile.png` — radial epsratio profile (when available)
- `richardson.png` — convergence trace (when available)

Templates and automatic dossier generation:

- `scripts/generate_excluded_run_dossiers.py`




## Required per-run dossier contents

For every entry in `index.csv` (EXCLUDED or DIAGNOSTIC), a dossier directory `supplement/excluded_runs/<run_id>/` is expected to contain:

- `diagnosis.txt` (human-readable reason and thresholds hit)
- at least one diagnostic plot (e.g., `residual_trace.png` and/or `epsratio_profile.png`)
- provenance pointers to raw artefacts via `data_ids` in `index.csv` (e.g., `outputs/runs/<run_id>/...`)

If the full run set is regenerated, dossiers can be (re)built automatically from the run outputs and `index.csv` using:

```bash
python scripts/generate_excluded_run_dossiers.py --index supplement/excluded_runs/index.csv --outdir supplement/excluded_runs
```

This ensures that the audit trail scales to the complete Monte‑Carlo ensemble without manual curation.


## Added stress-test dossiers (toy EOS)

The following toy-EOS stress-test runs are excluded from headline inference but provided as transparency dossiers:

- `Poly2toy_A_baseline` → `Poly2toy_A_baseline/diagnosis.txt` (+ `diagnostic_plot.png`)
- `Poly2toy_B_legacy` → `Poly2toy_B_legacy/diagnosis.txt` (+ `diagnostic_plot.png`)
- `Poly2toy_C_sigma_chi` → `Poly2toy_C_sigma_chi/diagnosis.txt` (+ `diagnostic_plot.png`)
