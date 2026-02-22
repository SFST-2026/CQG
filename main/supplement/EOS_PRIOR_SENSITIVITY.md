# EOS / Prior Sensitivity — Minimum reader-facing checks

This supplement documents a compact set of **three** robustness checks for the headline (Variant A) results:
1. **EOS spread:** repeat the headline σ-scan for at least SLy and AP4 (soft vs stiff baseline).
2. **Prior sanity:** re-evaluate the headline σ-range under a narrow vs wide prior on σ (and, if applicable, nuisance parameters).
3. **Regulator sensitivity:** repeat a small canonical subset under two regulator settings to bound discretization/regularization systematics.

# EOS / Prior Sensitivity — Minimal headline robustness checks

This supplement documents **minimal, high-leverage robustness checks** expected by readers when headline neutron-star / GW-target numbers depend on modelling choices.

The main manuscript’s headline results use **Variant A** and the canonical EOS set (SLy, AP4). The checks below are designed to show that qualitative trends and headline-level shifts are not artefacts of a single EOS choice or a single narrow prior.

## Check 1 — EOS spread (canonical soft vs stiff baselines)

**Goal:** demonstrate that the direction/magnitude of the SFST-induced \(\Lambda(M)\) shift is stable across representative EOS baselines.

- Baselines: SLy (softer) and AP4 (stiffer).
- Output: overlay plot of \(\Lambda(M)\) and \(\Lambda_{1.4}\) vs \(\sigma\) for both EOS.

Script entry point:

- `scripts/eos_sensitivity_demo.py`

Expected artefacts:

- `figures/eos_sensitivity_overlay.pdf/png`
- `supplement/tables/eos_sensitivity_summary.csv`

## Check 2 — Prior width sanity (narrow vs wide \(\sigma\) prior)

**Goal:** show that any inferred/illustrative \(\sigma\) range used for “headline” plots is not purely prior-driven.

- Priors: a narrow prior around the nominal perturbative regime (e.g. \(\sigma\in[\sigma_0\pm\Delta]\)) and a wider prior spanning stress-test regimes.
- Output: prior vs posterior overlay (or reweighted summary) for \(\Lambda_{1.4}\) targets.

Script entry point:

- `scripts/prior_sanity_demo.py`

Expected artefacts:

- `figures/prior_width_overlay.pdf/png`
- `supplement/tables/prior_width_summary.csv`

## Check 3 — Regulator / matching sensitivity (bounded by Variant A gates)

**Goal:** show that the headline trend is stable under reasonable regulator/matching variations when **epsratio gating** is enforced.

- Variation: scan of regulator settings documented in the repository (`scan_wrappers.py`).
- Output: band of \(\Lambda_{1.4}\) vs \(\sigma\) or \(M\! -\! R\) vs \(\sigma\) across regulator settings, with the accepted-run gate highlighted.

Script entry point:

- `scripts/regulator_sensitivity_demo.py`

Expected artefacts:

- `figures/regulator_sensitivity_band.pdf/png`
- `supplement/tables/regulator_sensitivity_summary.csv`

## Notes for readers

These checks are intentionally lightweight and are meant to bound the **dominant systematic degrees of freedom** (EOS baseline, prior width, and regulator/matching choices). They do not replace a full microphysical EOS refit, which is outside the scope of the present paper.


> One-glance overview: see `EOS_PRIOR_SANITY_TABLE.md` for a 6-row sanity summary (SLy, AP4, +1 bracket) × (narrow/wide prior).


## Additional EOS checks (stiff/soft bracketing)

We include two further representative EOS as bracketing checks beyond the canonical set, using the same numerical tolerances and priors as for the baseline/SFST comparison:

| EOS | Mmax (base→SFST) | R1.4 (base→SFST) [km] | Λ1.4 (base→SFST) | max_epsratio (SFST) | Note |
|---|---:|---:|---:|---:|---|
| H4-PP(Read2009) | 2.044 → 1.957 (-4.2%) | 12.76 → 7.84 (-38.5%) | 1341.8 → 20.6 (-98.5%) | 0.06 | stiff-bracket (H4) |
| WFF1-PP(Read2009) | 1.666 → 1.611 (-3.3%) | 6.60 → 6.33 (-4.0%) | 19.3 → 5.1 (-73.7%) | 0.06 | soft-bracket (WFF1) |

These bracketing checks are reported as a sensitivity sanity test (not as a definitive EOS selection). Full posterior/fit artifacts are available via the snapshot and the run IDs in the table.
