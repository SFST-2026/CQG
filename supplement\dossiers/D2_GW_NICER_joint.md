# D2 — Joint GW + NICER Bayesian inference (consistency test)

## Goal
Test whether a single σ can shift GW tidal posteriors and NICER R(M) posteriors consistently **while remaining perturbative** (epsratio≤0.10).

## Forward model (scaffold in this snapshot)
Uses precomputed σ-scan sensitivities as a fast approximation; upgrades to full grids \(R(M;\sigma)\), \(\Lambda(M;\sigma)\) are documented in `docs/gw_reweighting_and_joint_inference.md`.

## Deliverables
- Script: `scripts/joint_gw_nicer_inference.py`
- Config: `configs/gw_events.yaml`, `configs/nicer_targets.yaml`
- Output: `artefacts/joint_sigma_posterior_*.csv`, `artefacts/joint_bayes_factor_*.txt`
