#!/usr/bin/env python3
"""
toy_model_chi_ou.py

Reproducible toy model used in Supplement: an Ornstein–Uhlenbeck (OU) flux field
with update-rate Gamma. We compute the retarded susceptibility and a proxy
"inertial kernel curvature" that yields the mapping m_vac ~ g^2 * chi / Gamma.

This file intentionally stays lightweight and deterministic (no external data).
"""
from __future__ import annotations
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

def chi_retarded_ou(omega: np.ndarray, Gamma: float) -> np.ndarray:
    """Retarded susceptibility of OU process to a source: 1/(-i omega + Gamma)."""
    return 1.0 / (Gamma - 1j*omega)

def kernel_curvature_proxy(Gamma: float) -> float:
    """
    Proxy for d^2/domega^2 Re[chi(omega)] at omega=0.
    For chi = 1/(Gamma - i omega), Re[chi] = Gamma/(Gamma^2 + omega^2).
    d^2/domega^2 Re[chi] at 0 = -2/Gamma^3.
    We take chi_proxy := 2/Gamma^2 so that m_vac ~ g^2 * chi_proxy / Gamma.
    """
    return 2.0/(Gamma**2)

def main():
    out_dir = Path("outputs/toy_model_chi")
    fig_dir = Path("figures/toy_model_chi")
    out_dir.mkdir(parents=True, exist_ok=True)
    fig_dir.mkdir(parents=True, exist_ok=True)

    Gammas = np.logspace(-3, 3, 200)
    chi_proxy = np.array([kernel_curvature_proxy(G) for G in Gammas])
    # define sigma := g^2/Gamma * chi_ref (chi_ref=1)
    g = 1.0
    sigma = (g**2)/Gammas  # chi_ref=1 convention
    m_vac_proxy = (g**2) * chi_proxy / Gammas

    df = pd.DataFrame({
        "Gamma": Gammas,
        "chi_proxy": chi_proxy,
        "sigma_mapping_g2_over_Gamma": sigma,
        "m_vac_proxy_g2_chi_over_Gamma": m_vac_proxy,
        "scaling_note": "chi_proxy=2/Gamma^2; m_vac_proxy=g^2*chi_proxy/Gamma ~ g^2/Gamma^3"
    })
    df.to_csv(out_dir/"chi_toy_scan.csv", index=False)

    plt.figure(figsize=(6,4))
    plt.loglog(Gammas, chi_proxy, label=r"$\chi_{\rm toy}\propto \Gamma^{-2}$")
    plt.loglog(Gammas, m_vac_proxy, label=r"$m_{\rm vac}\propto g^2\,\chi/\Gamma\propto \Gamma^{-3}$")
    plt.xlabel(r"update rate $\Gamma$")
    plt.ylabel("proxy magnitude (arb. units)")
    plt.title("Toy OU flux model: susceptibility scaling")
    plt.legend()
    plt.tight_layout()
    plt.savefig(fig_dir/"chi_toy_scaling.png", dpi=300)
    plt.savefig(fig_dir/"chi_toy_scaling.pdf")
    plt.close()

if __name__ == "__main__":
    main()
