# Physical plausibility diagnostic: eps_vac,inertial / eps_ref

We use the dimensionless ratio

\[
\epsilon_{\mathrm{vac,inertial}}(r) / \epsilon_{\mathrm{ref}}(r)
\]

as a reviewer-facing plausibility and scaling check for the chosen σ,χ conventions.

## What we report
- A per-run profile plot: `plots/epsratio_<EOS>_<case>.png`
- A run-level scalar: `epsratio_absmax = max_r |eps_vac,inertial/eps_ref|`, stored in `outputs/epsratio_summary.csv`

## How we use it
- We treat results as physically interpretable only when the ratio stays within a conservative bound
  (default: `epsratio_absmax_threshold = 1.0` in `config/validate_config.yaml`), and we flag any run that exceeds it as DIAGNOSTIC.
- We keep the bound conservative for peer review; if we tighten/relax it, we record the change in Git history and in the audit trail.

## How to reproduce
1. Generate a profile CSV containing `r`, `eps_ref`, `eps_vac_inertial`.
2. Run:
   `python3 scripts/plot_eps_ratio.py --profile <csv> --eos <EOS> --case <case_tag>`
3. Validate:
   `python3 scripts/validate_run.py --runs outputs/runs_summary.csv`
