# EOS/Prior sanity grid (compact)

This compact table is intended as a “quick look” sanity check that the headline SFST Variant A shifts are not artifacts of a single EOS choice or prior setting. The **full posterior distributions** and additional EOS/prior details are provided elsewhere in the Supplement.

**Note:** In the lightweight repository bundle, the “narrow/wide prior” rows may coincide if only deterministic canonical runs are available. When posterior runs are produced, the build script regenerates this table from posterior summaries under the corresponding prior definitions.

Table columns: baseline (Standard model) vs SFST Variant A at the same numerical tolerances; Δ values are SFST − baseline.

| EOS | Prior | ΔM_max [M☉] | ΔR_1.4 [km] | ΔΛ_1.4 | Data snapshot ID |
|---|---:|---:|---:|---:|---|
| SLy | narrow | -0.0704 | +1.356 | +23.4 | data/snapshots/snapshot_c04378d8b099.tar.gz.tar.gz |
| SLy | wide | -0.0704 | +1.356 | +23.4 | data/snapshots/snapshot_c04378d8b099.tar.gz.tar.gz |
| AP4 | narrow | -0.0650 | -0.146 | -144.4 | data/snapshots/snapshot_c04378d8b099.tar.gz.tar.gz |
| AP4 | wide | -0.0650 | -0.146 | -144.4 | data/snapshots/snapshot_c04378d8b099.tar.gz.tar.gz |
| MPA1 | narrow | -0.0735 | -0.189 | -213.4 | data/snapshots/snapshot_c04378d8b099.tar.gz.tar.gz |
| MPA1 | wide | -0.0735 | -0.189 | -213.4 | data/snapshots/snapshot_c04378d8b099.tar.gz.tar.gz |

Generated from `outputs/tables/eos_prior_sanity_grid.csv`.
