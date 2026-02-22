# Precision-tests add-on (Appendix P)

This folder contains *conservative*, model-agnostic constraint utilities for external precision observables:
- muon g-2 (a_mu)
- CDF II W mass
- representative RK input

**Important:** The code here does **not** assume SFST/QFIS explains these anomalies. Instead, it provides a
reproducible workflow to translate a *user-chosen* SM reference difference into a bound on a minimal effective
coefficient, and a scaffold for future sector-level matching.

Run:
```bash
python precision_tests/scripts/constraints.py --show
```
