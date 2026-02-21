# Major-revision risk checklist (prioritized) and mitigation

This note is intended as a **reviewer-facing checklist**: it enumerates the remaining major-revision triggers and the concrete, auditable mitigation steps implemented in this repository.

## Major-revision triggers (prioritized)

1. **Unresolved diagnostic runs** without documented stabilization attempts or a clean, auditable exclusion.
2. **Variant B in headline reporting** without an independent source-matching coefficient (`c_src`) **or** without clear labeling as exploratory.
3. **Missing compact main figures**: (i) ΔΛ₁.₄(σ) comparison for SLy/AP4 with Quadratic/MC envelopes and a conservative observational overlay, and (ii) three Richardson convergence plots in the Main.
4. **Insufficient toy calibration / robustness tests**: reviewers often request an explicit, reproducible χ-calibration (or additional numerical stress tests).

## Mitigation steps (highest leverage first)

### A) Targeted re-runs for all δ_total > 50% cases (high leverage)
- Run staged refinement attempts using:
  - grid refinement (`grid_factor`), stricter Newton tolerances (`newton_tol`), and (optionally) an alternative solver/integrator.
- **Every attempt** is logged to:  
  `outputs/diagnostics/<orig_run_id>/refinement_log.json`
- If stabilization succeeds: mark **RESOLVED** (or **STRESS_RESOLVED**) in the audit trail.
- If not stabilizable after retries: mark **UNRESOLVED** and **exclude from headline statistics**, retaining full logs for audit.

**Quick-start (5-case smoke test):** see `README_refinement.md` → “Quick-start: test refinement for 5 diagnostic cases”.

### B) Variant-B gate (EFT consistency) (high leverage)
- Methods statement: **Variant B only with an independent source operator and matching coefficient `c_src`; otherwise Variant B is exploratory and reported only in the Supplement.**
- Appendix: operator bookkeeping, matching, and the rationale for Variant A as the controlled implementation.
- Headline outputs must be generated from **Variant A accepted runs only**.

### C) Main-text figures/tables (medium leverage)
- ΔΛ₁.₄(σ) comparison for SLy/AP4 with Quadratic/MC envelopes + conservative observational overlay.
- Three Richardson plots in the Main (representative SLy/AP4 + one toy/extra case).
- Compact main table: `M_max, R_1.4, Λ_1.4, ΔΛ and %Δ` (relative to baseline point).

### D) Toy calibration visibility (medium leverage)
- Reproducible χ-calibration script: `scripts/toy_model_chi_ou.py`
- Supplement figure output (see `figures/` and Supplement references in the manuscript).
- Methods pointer: a short sentence linking to the toy calibration and explaining the measurement procedure.

### E) Public archive snapshot (low effort, high trust)
- Create an annotated git tag for submission (e.g., `v1.0.0-submission`).
- Archive on Zenodo and obtain a DOI.
- Record the DOI in the manuscript’s Data & Code Availability section and (optionally) provide checksums.

## “Do now” recommendation (high leverage)
Run local refinement for 5–10 diagnostic cases and update:
- `outputs/audit_index.csv`
- `outputs/scan_grid.csv` (if used)
- `outputs/headline_without_diagnostics.csv` (regenerate after exclusions)

Then ensure Main figures/tables match the updated, accepted-only dataset.
