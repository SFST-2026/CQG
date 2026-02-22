# WFaktor diagnostic (definition, thresholds, and reporting)

## Definition
Let X_base(r) denote the solver’s dimensionless internal variable(s) for the baseline run and X_σ(r) the same variable with the σχ insertion. We define the pointwise amplification

WFaktor(r) = |X_σ(r) − X_base(r)| / max(ε_machine, |X_base(r)|).

We report a single run-level WFaktor as the maximum over the resolved domain:

WFaktor_max = max_r WFaktor(r),

and I also record the radius r_max where the maximum occurs.

## Computation steps
1. We compute baseline and inserted profiles on the same grid and with identical solver tolerances. 
2. We evaluate X_base(r) and X_σ(r) at grid points; if grids differ we use the same interpolation both ways. 
3. We use a small floor ε_machine (default 1e−16) to avoid division by zero. 
4. We store WFaktor_max and r_max, and I save WFaktor(r) as a profile plot.

## Acceptance / exclusion rule
- **ACCEPT** if solver convergence criteria are met and WFaktor_max ≤ 1e2. 
- **FLAG** if 1e2 < WFaktor_max ≤ 1e4; I inspect Newton residual histories and grid convergence. 
- **EXCLUDE** from summary statistics if WFaktor_max > 1e4 or if large WFaktor correlates with non‑convergent Newton residuals or failed CFL-like checks.

## Repository outputs
- outputs/wfaktor_summary.csv 
- plots/deltaM_vs_wfaktor.png 
- per-run bundles: outputs/diagnostics/<EOS>_<case>/wfaktor_profile.png
