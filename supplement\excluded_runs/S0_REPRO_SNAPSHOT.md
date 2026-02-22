# Supplement S0 — Reproducibility snapshot and audit links

This repository snapshot is intended to be reviewer-runnable without external dependencies beyond Python 3 and (optionally) Docker.

## What to check (fast)

- **Docker recipe:** `Dockerfile` (root). Build and run notes are in `README.md`.
- **Smoke-test log (this snapshot):** `supplement/ci_smoketest.log`
- **Provenance manifest (machine + commands + hashes):** `PROVENANCE.txt` (root) and `outputs/provenance.txt`
- **CI workflow template:** `.github/workflows/ci.yml` (runs the same smoke test on each push/PR)

## One-command local reproduction (canonical)

```bash
bash scripts/smoke_test.sh
```

This script runs a minimal end-to-end pipeline and writes a short log (also archived as `supplement/ci_smoketest.log`).

## Audit trail pointers

- Per-run diagnostics: `outputs/diagnostics/<run_id>/`
- Diagnostic/excluded dossiers (human-readable): `supplement/diagnostic_dossiers/INDEX.md`
- Main validation checklist: `SUBMISSION_CHECKLIST.md`
