# CI artefacts (fast profile)

The repository snapshot includes machine-generated artefacts produced by the **fast CI** profile to support reviewer verification:

- `outputs/accepted.csv` — headline-eligible cases (post-validation)
- `outputs/diagnostic.csv` — cases kept as **DIAGNOSTIC** (paired reporting incl./excl. diagnostics)
- `outputs/audit_index.csv` — indexed remediation log for runs with `δ_total > 50%` (including EXCLUDE decisions)
- `outputs/audit_trail.csv` — row-level audit trail (inputs → solver settings → outcome)

For any run that required remediation attempts, see the human-readable record:

- `outputs/diagnostics/<run_id>/diagnosis.txt`

These files are referenced from the manuscript Supplement section **“CI artefacts (repository snapshot)”**.
