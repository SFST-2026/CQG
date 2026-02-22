# Conventions & Units (single source of truth)

- Geometrized units: **G = c = 1**, length unit = **cm** in the reference solver.
- Solar mass in geom-cm: M_sun_geom_cm = G M_sun / c^2
- Pressure/energy density conversion: P_geom = P_cgs * (G/c^4)

Kernel normalization:
- we define S_eff[x] = (1/2) ∫ (dω/2π) x(-ω) K(ω) x(ω)
- Expand: K_R(ω) = K_R(0) + (1/2) m_vac ω^2 + O(ω^4)
- Therefore: m_vac := (d^2 K_R / dω^2)|_{ω=0} and **C_conv = 1** under this fixed convention.

IMPORTANT:
- The `delta_inertia` insertion in the reference TOV code is a **paper-derived toy mapping**:
 ε -> (1 + delta_inertia) ε, pressure unchanged.
 Replace this mapping with the manuscript’s exact insertion prescription once available.


## Sigma*Chi insertion modes
- Variant A (default): affects only inertial factor (ε+P) via ε_inertial = ε + ε_vac_inertial; dm/dr uses ε only.
- Variant B: set include_in_gravity=true to also add ε_vac_inertial to gravitational source.


## compute_tov_case integration

For HPC/cluster runs and (g,Γ) scans, see `docs/INTEGRATION_COMPUTE_TOV_CASE.md` and the Slurm templates in `slurm/`.


### Quick smoke test

Run a minimal end-to-end scan (synthetic outputs unless you wire a solver) with:

```bash
SFST_DRYRUN=1 make scan_gGamma_small
```

See `scripts/scan_gGamma_small.py` and `slurm/params_minimal.csv`.
