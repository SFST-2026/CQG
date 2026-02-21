# Reviewer Addendum (One Page)

This addendum summarizes (i) **what changes relative to the standard theory**, (ii) **how headline results are reported (Quadratic/MC with 5–95% bands)**, and (iii) **how outliers/diagnostics are audited**, with direct pointers to repository artifacts.

## A. What changes vs. the standard theory (where the modification enters)

We distinguish two insertion hypotheses used throughout the repository:

- **Variant A (baseline; headline interpretation):** the vacuum-induced correction is inserted **only in the inertial coupling** (structure response), leaving the gravitational source term unchanged.
- **Variant B (`B_exploratory`; sensitivity stress test):** the same correction is additionally inserted **on the source side** (exploratory; potential double-counting without independent EFT operators).

**Newtonian / slow-motion limit (schematic):**
- Standard:  \( m\,\mathbf{a} = -m\nabla\Phi\,,\quad \nabla^2\Phi = 4\pi G\rho\,.\)
- Variant A (inertial only):  \( (m+m_{\rm vac})\,\mathbf{a} = -m\nabla\Phi\,,\quad \nabla^2\Phi = 4\pi G\rho\,.\)
- Variant B (exploratory; inertial+source):  \( (m+m_{\rm vac})\,\mathbf{a} = -(m+\delta m_{\rm vac})\nabla\Phi\,,\quad \nabla^2\Phi = 4\pi G(\rho+\delta\rho_{\rm vac})\,.\)

Repository marking:
- Variant B runs are explicitly labeled as **`variant=B_exploratory`** in `outputs/runs_summary.csv`.
- Direct A vs. B comparison artifacts:
  - `figures/variantA_vs_B_exploratory_lambda1p4.png`
  - `figures/variantA_vs_B_exploratory_deltaLambda_sigma_panel.png`
  - `outputs/variant_ab_comparison.csv`

## B. Headline reporting: Quadratic fit + Monte-Carlo (5–95%) and paired “with/without diagnostics”

To avoid isolated linear percent-claims, headline statements are reported as:
- **Quadratic-fit central tendency** across the \(\sigma\)-grid (min/median/max), and
- **Monte-Carlo uncertainty bands** (5–95%) from the run-level envelopes.

Paired headline tables (reviewer-facing):
- Including DIAGNOSTIC runs: `outputs/headline_with_diagnostics.csv`
- Excluding DIAGNOSTIC runs: `outputs/headline_without_diagnostics.csv`

Paired headline figure:
- `figures/lambda1p4_paired_including_excluding_clipped.png`

## C. Outlier audit & remediation (δ_total > 50%)

Runs with large total deviations (e.g. \(\delta_{\rm total} > 50\%\)) are either:
1. **Stabilized by re-runs** (grid refinement \(n\to 2n\), `epsabs=epsrel=1e-12`, `max_iter=400`, Newton damping), or
2. **Excluded** if stabilization fails, with an explicit audit trail.

Audit index (single entry point):
- `outputs/audit_index.csv`  (includes per-run status, reasons, and key diagnostics)

Per-run evidence:
- `outputs/diagnostics/<run_id>/diagnosis.txt`  (attempt log + flags + summary)
- Additional diagnostic artifacts may appear per run (e.g., Richardson plots, residuals).

Validation entry point:
```bash
python scripts/validate_run.py --runs outputs/runs_summary.csv
```

## D. epsratio plausibility bands (interpretability gating) + literature anchoring

We gate physical interpretability using `max_r |epsratio|` with bands:
- **≤ 0.10** (interpretable / perturbative),
- **0.10–0.30** (stress test / sensitivity context),
- **> 0.30** (DIAGNOSTIC / excluded).

Representative profiles are archived as:
- `plots/epsratio_<EOS>_<case>.png`

Literature anchoring and quantified scaling rationale are included in the manuscript and supported by:
- `docs/references/tidal_refs.bib` (Hinderer 2008; Flanagan & Hinderer 2008; Hinderer et al. 2010)

## E. Numerical robustness: convergence evidence

Representative convergence (Richardson) plots are linked from the manuscript and available under:
- `outputs/diagnostics/<run_id>/richardson.png` (for selected EOS/cases)

## F. Public archiving plan (pre-submission)

The repository contains a `zenodo_deposit/` helper folder to finalize a public archive before submission:
- Create a **git tag** for the submission snapshot
- Deposit on Zenodo and record the **DOI** in the manuscript’s Data/Code Availability statement
- Preserve CI artifacts (`accepted.csv`, `diagnostic.csv`, `audit_trail.csv`) as release assets

---
**Bottom line:** Variant A is the baseline for headline interpretation; Variant B is explicitly labeled exploratory and shown side-by-side on the same \(\sigma\)-grid. Headline results are quadratic/MC with 5–95% bands, and diagnostics/outliers are fully audited with per-run `diagnosis.txt`.
