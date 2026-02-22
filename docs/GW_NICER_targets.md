# SFST: quantitative falsifiable targets (GW/NICER)

This note defines a **data-facing** mapping from an observed tidal-deformability shift to a required SFST parameter, using the measured numerical sensitivities from the archived σ-scans.

## 1. Linearized mapping (per EOS)

For a given EOS, define the measured slope

S_Λ(EOS) ≡ ΔΛ₁.₄ / Δσ,

computed from the archived scan points (see `outputs/runs_summary.csv` / `outputs/scan_summary.csv`).

Given an observed deviation ΔΛ_obs (absolute, not percent), the required SFST parameter is estimated as:

σ_req ≈ ΔΛ_obs / S_Λ(EOS).

A run is **interpretable (perturbative)** only if:

max_r |epsratio(r)| ≤ 0.10,

and is flagged STRESS (0.10–0.30) or DIAGNOSTIC (>0.30) otherwise.

## 2. Representative numeric predictions (from this snapshot)

Using the accepted `C_sigma_chi` runs at σ=0.06 and the σ=0 baselines:

- **AP4:** baseline Λ₁.₄ ≈ 540.1; measured ΔΛ₁.₄(0.06) ≈ -144.4.
  Linear prediction: ΔΛ₁.₄(σ=0.02) ≈ -48.1, ΔΛ₁.₄(σ=0.04) ≈ -96.3.

- **SLy:** baseline Λ₁.₄ ≈ 455.1; measured ΔΛ₁.₄(0.06) ≈ 23.4.
  Linear prediction: ΔΛ₁.₄(σ=0.02) ≈ 7.8, ΔΛ₁.₄(σ=0.04) ≈ 15.6.

These are **falsifiable targets**: if GW+NICER posteriors require σ outside the perturbative band (σ≳0.10 in this proxy model), the simple SFST scaling hypothesis is disfavored.

## 3. Near-term tests (1–3 years)

- **GW posterior reweighting:** reweight GW170817 / later BNS posterior samples under the SFST-predicted Λ(M) deformation and compute Bayes factors.
- **NICER updates:** jointly constrain R(M) and Λ(M) deformations with new NICER radius posteriors.
- **Consistency gates:** only interpret samples passing `epsratio≤0.10` and stable convergence order (p consistent) under tighter tolerances.

## 4. Mandatory robustness protocol for speculative matches

Before making any speculative “match” claim in the manuscript:

1. epsratio ≤ 0.10 (or label as stress/diagnostic).
2. Richardson-order p consistent (and at least two refinement levels archived).
3. WFaktor within configured bounds.
4. Re-run with tighter tolerances (rtol/atol) to confirm stability.
5. Repeat with at least one alternative EOS family to quantify EOS-systematic shifts.

See `SUBMISSION_CHECKLIST.md` for the reader-facing checklist.
