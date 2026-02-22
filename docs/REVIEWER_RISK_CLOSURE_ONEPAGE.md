# readers risk-closure note (one page)

This note summarizes how the submission closes the three remaining readers risks: **(i) EFT operator bookkeeping / Variant‑B gate**, **(ii) outliers with δ_total ≫ 50%**, and **(iii) the Ambjørn–Watabiki (AW) connection**. It is intentionally short and points to auditable artifacts.

## 1) EFT operator bookkeeping and Variant‑B gate (closed)
**What is controlled (headline basis).** Headline claims use **Variant A (inertial‑only insertion)** and only **ACCEPTED** runs as classified by `scripts/validate_run.py`.

**Why Variant A is controlled.** The induced inertial coefficient is matched from the low‑frequency expansion of the retarded kernel
\[
K_R(\omega)=K_R(0)+\tfrac12 m_{\mathrm{vac}}\,\omega^2+\mathcal{O}(\omega^4),\qquad
m_{\mathrm{vac}}\equiv \left.\frac{d^2K_R}{d\omega^2}\right|_{\omega=0}\approx g^2\,\chi/\Gamma .
\]
This follows from integrating out the flux field coupled via the interaction operator \(\mathcal{O}_{\mathrm{int}}\). See `docs/APPENDIX_EFT_MATCHING.md` (Appendix A.7).

**Variant‑B policy (gate).** Variant B (inertial + gravitational source insertion) is **exploratory** unless an **independent source operator** \(\mathcal{O}_{\mathrm{src}}\) with its own matching coefficient \(c_{\mathrm{src}}\) is introduced and matched. Without this, inserting the same coefficient into the source **double‑counts** the EFT effect and Variant B is excluded from headline statistics.
- Gate text & operator list: `docs/APPENDIX_EFT_MATCHING.md` (A.7)
- Variant labels in data: `outputs/runs_summary.csv` (`variant=B_exploratory`)

## 2) Outliers / δ_total ≫ 50% (closed via stabilize-or-exclude protocol)
**Risk.** Extreme δ_total values can dominate quadratic fits and undermine headline robustness if left unresolved.

**Policy.** For every run with δ_total > 50%:
1) attempt stabilization (grid refinement \(n\to 2n\), `epsabs=epsrel=1e-12`, `max_iter=400`, Newton damping);
2) document each attempt in `outputs/diagnostics/<run_id>/diagnosis.txt`;
3) if stabilization fails in the snapshot, mark **EXCLUDED** and index it in `outputs/audit_index.csv`.

**Auditable artifacts.**
- Machine-readable plan: `outputs/rerun_plan_delta_total_gt50.csv`
- Controller script: `scripts/targeted_rerun_outliers.py`
- Per-run logs: `outputs/diagnostics/<run_id>/diagnosis.txt`
- Summary: `outputs/audit_index.csv`, `outputs/audit_trail.csv`
- Headline CSVs exclude EXCLUDED cases by construction.

## 3) Ambjørn–Watabiki (AW) link (closed by precise scope + conjecture label)
**What we claim.** AW is used only as **qualitative motivation**: microscopic topology can affect response functions/susceptibilities.

**What we do NOT claim.** We do **not** import AW critical exponents or claim a quantitative mapping from DT/2D quantum gravity to neutron‑star interiors. Any such extrapolation is explicitly labeled **conjecture**.

**Auditable artifacts.**
- Toy susceptibility calibration (reproducible):  
  Script `scripts/toy_model_chi_ou.py`, outputs `outputs/toy_model_chi/chi_toy_scan.csv`, figure `figures/toy_model_chi/chi_toy_scaling.png`
- Precise AW scope and citations: `supplement/SUPPLEMENT_TOYMODEL_CHI_AW.md`

## 4) Practical readers checklist (quick)
- Headline uses Variant A + ACCEPTED only: `outputs/headline_without_diagnostics.csv`
- Transparency including diagnostics: `outputs/headline_with_diagnostics.csv`
- Outlier audit index: `outputs/audit_index.csv`
- Variant‑B is exploratory unless independently matched: `docs/APPENDIX_EFT_MATCHING.md` (A.7)
- Toy χ calibration is reproducible: `scripts/toy_model_chi_ou.py`



## Added for readers risk closure (v64)
- Main figure: outputs/figures/lambda1p4_vs_sigma_obsband_sly_ap4.png (quadratic/MC + illustrative observational band; Variant A only).
- Main figure: outputs/figures/richardson_triplet_sly_ap4_poly2.png (three Richardson plots).
- Main table CSV: outputs/tables/compact_comparison_table_sly_ap4.csv.
- Refinement logs: outputs/diagnostics/<run_id>/refinement_log.json for all δ_total>0.50 or DIAGNOSTIC/FAILED.
