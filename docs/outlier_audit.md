# Outlier audit (headline vs diagnostic)

We treat any run as **DIAGNOSTIC** (not used for headline claims) if one or more of the following holds:

- δ_total > 50% for any headline observable (M_max, R_1.4, Λ_1.4).
- Newton convergence failure or residual plateau above my declared tolerance.
- WFaktor_max above my EXCLUDE threshold.
- Richardson grid-ladder does not show monotone convergence or yields an unstable extrapolation.

For every DIAGNOSTIC/EXCLUDED run we provide:

- `outputs/diagnostics/<EOS>_<case>/run.log`
- `outputs/diagnostics/<EOS>_<case>/residuals.png`
- `outputs/diagnostics/<EOS>_<case>/richardson.png`
- `outputs/diagnostics/<EOS>_<case>/wfaktor.png`
- `outputs/diagnostics/<EOS>_<case>/diagnosis.txt`

And I record a machine-readable entry in `outputs/audit_trail.csv`.
