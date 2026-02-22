# Diagnostics index (outliers and flagged cases)

For each run with δ_disc or δ_total > 100% (or otherwise flagged by WFaktor/solver diagnostics), I place a bundle in:

- outputs/diagnostics/<EOS>_<case>/

Each bundle contains:
- richardson_extrapolation.png
- newton_residuals.png
- wfaktor_profile.png
- run.log
- diagnosis.txt (short explanation: underresolution, EOS pathology, or bug)

Headline tables exclude δ_total > 100% cases by default; I still report them here with full diagnostics.


## CI artefacts

See `supplement/CI_ARTIFACTS.md` for the list of CI-produced CSV artefacts (accepted/diagnostic/audit logs) shipped with this snapshot.


## Toy-model χ calibration and Ambjørn–Watabiki motivation
- `supplement/SUPPLEMENT_TOYMODEL_CHI_AW.md` (reproducible toy model + explicit conjecture labeling)

- Risk-closure summary: `supplement/SUPPLEMENT_RISK_CLOSURE.md`
