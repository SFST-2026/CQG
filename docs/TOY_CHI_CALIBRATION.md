# Toy χ calibration (OU flux model)

This repository includes a lightweight, reproducible calibration of the flux susceptibility χ in the Ornstein–Uhlenbeck (OU) toy model.

## How to reproduce

From the repository root:

```bash
python scripts/toy_model_chi_ou.py
```

This generates:

- `figures/toy_model_chi/chi_toy_scaling.png` — scaling check for χ(Γ) / kernel coefficient extraction.
- `outputs/toy_model_chi/chi_toy_scan.csv` — machine‑readable scan data.

## Measurement procedure (short)

1. Simulate OU flux realizations for a grid of update rates Γ with fixed noise strength.
2. Extract the low‑frequency retarded response and fit the kernel expansion
   \(K_R(\omega)=K_R(0)+\tfrac12 m_{\rm vac}\,\omega^2+\mathcal{O}(\omega^4)\).
3. Define \(\chi\) by matching the measured \(m_{\rm vac}\) to the working EFT mapping used in the paper
   \(m_{\rm vac}\approx g^2\chi/\Gamma\) (convention choice described in the Appendix).
4. Store per‑Γ results and the fitted slope in the CSV and plot.

The toy model is intended as a plausibility / calibration aid and does **not** replace the EFT matching argument.
