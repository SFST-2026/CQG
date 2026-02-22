# Minimal model-comparison quantification (reader-facing)

This note provides minimal quantitative metrics to accompany the visual posterior comparisons.
Use at least one of the following, computed under identical priors/conditions for SM vs SFST (Variant A):

- **Posterior overlap** (e.g., integral overlap for a key 1D marginal such as R1.4 or Λ1.4)
- **Δχ² / ΔlogL** for a representative summary statistic (if a likelihood is available)
- **Bayes factor** (if you have evidences or a consistent approximation)

## Recommended minimal deliverable

- A short table reporting, for each EOS family used in the headline results, a **single scalar** metric (overlap or Δχ²) plus the corresponding data snapshot ID.
- A figure panel in the Supplement showing the full posteriors (SM vs SFST) for at least one key observable (e.g., R1.4 or Λ1.4).

## Reproducibility

- Store inputs as `data/figX_inputs/` or `data/snapshots/snapshot_c04378d8b099.tar.gz.tar.gz`.
- Report the snapshot ID, git commit, Docker digest, and seed in `SUPPLEMENT_FIGX_PROVENANCE.md`.

