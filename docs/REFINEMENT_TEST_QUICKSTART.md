# Refinement quickstart (local test: 5 diagnostic cases)

This page provides a copy/paste workflow to **run a small, local refinement test** on five diagnostic cases and update the audit index.

It assumes the repository root is your current working directory and that your solver entrypoint accepts:

```bash
python run_tov.py --eos <EOS> --sigma <SIGMA> --run-tag <RUN_TAG> --grid-factor <GRID_FACTOR> --newton-tol <NEWTON_TOL>
```

## 1) Create a small audit list with 5 diagnostic rows

```bash
mkdir -p outputs
awk -F, 'NR==1 || ($4=="DIAGNOSTIC" || $4=="FAILED" || $4=="PARSE_ERROR") {print $0}' outputs/audit_index.csv | head -n 6 > outputs/audit_index_small.csv
```

## 2) Run the controller locally (3 retries)

```bash
python3 scripts/refine_and_retry_cli.py --input outputs/audit_index_small.csv --mode local --n_retries 3 --wait_after_submit 5
```

What happens:

- For each run_id the controller attempts up to 3 retries with
  `grid_factor ∈ [1.5, 2.0, 3.0]` and `newton_tol ∈ [1e-6, 1e-7, 1e-8]`.
- Each attempt creates `outputs/diagnostics/<run_tag>/run.log` and (if produced by the solver) `summary.json`.
- A structured retry log is appended to `outputs/diagnostics/<orig_run_id>/refinement_log.json`.

## 3) Update the audit index from all summary.json files

```bash
python3 scripts/collect_results.py
mv outputs/audit_index_updated.csv outputs/audit_index.csv
```

## 4) Quick checks

```bash
ls -1 outputs/diagnostics | sed -n '1,50p'
jq . outputs/diagnostics/<ORIG_RUN_ID>/refinement_log.json
jq . outputs/diagnostics/<SOME_RUN_TAG>/summary.json
```

Status interpretation (as used by the controller):

- **RESOLVED**: `converged == true` and `max_epsratio ≤ 0.10`
- **STRESS_RESOLVED**: `converged == true` and `0.10 < max_epsratio ≤ 0.30`
- **UNRESOLVED / DIAGNOSTIC**: no convergence or `max_epsratio > 0.30` after all retries
