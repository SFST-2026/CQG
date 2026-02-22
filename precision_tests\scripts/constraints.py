#!/usr/bin/env python3
"""precision_tests/scripts/constraints.py

Minimal, conservative constraint module.
- Does NOT assume SFST/QFIS explains anomalies.
- Provides bound on an effective dipole coefficient C_mu from Δa_mu.
- Provides a simple χ^2 utility for (mW, RK) if a user supplies a model prediction.

Usage:
  python precision_tests/scripts/constraints.py --show
"""

from __future__ import annotations
import argparse, math, yaml, pathlib
from dataclasses import dataclass

ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "precision_inputs.yaml"

@dataclass
class AMuInput:
    value: float
    sigma: float

def load_inputs(path=DATA):
    with open(path, "r") as f:
        d = yaml.safe_load(f)
    return d

def bound_C_mu(delta_a_mu: float, sigma_delta: float, nsigma: float = 2.0):
    """Conservative bound on |C_mu| given Δa_mu ≃ Re(C_mu)."""
    return abs(delta_a_mu) + nsigma * sigma_delta

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--show", action="store_true")
    # Optional: user can specify a preferred SM reference difference:
    ap.add_argument("--delta_a_mu", type=float, default=None,
                    help="User-specified (a_mu(exp)-a_mu(SM)) in absolute units.")
    ap.add_argument("--sigma_delta", type=float, default=None,
                    help="Uncertainty on delta_a_mu (quadrature).")
    ap.add_argument("--nsigma", type=float, default=2.0)
    args = ap.parse_args()

    d = load_inputs()
    a_mu_exp = float(d["a_mu"]["value"])
    a_mu_sigma = float(d["a_mu"]["sigma"])

    if args.show:
        print("Loaded inputs from:", DATA)
        print("a_mu(exp) =", a_mu_exp, "+/-", a_mu_sigma)
        print("mW(CDF II) =", d["w_mass_cdf2"]["value_GeV"], "+/-", d["w_mass_cdf2"]["sigma_GeV"], "GeV")
        print("R_K(high q^2) =", d["R_K_highq2"]["value"], "+/- stat", d["R_K_highq2"]["sigma_stat"], "+/- syst", d["R_K_highq2"]["sigma_syst"])
        print()

    if args.delta_a_mu is None or args.sigma_delta is None:
        print("No delta_a_mu provided. This script intentionally avoids picking a single SM prediction.")
        print("Provide --delta_a_mu and --sigma_delta from your chosen SM reference to compute a conservative |C_mu| bound.")
        print("Example: python precision_tests/scripts/constraints.py --delta_a_mu 2.5e-9 --sigma_delta 6e-10")
        return

    cmax = bound_C_mu(args.delta_a_mu, args.sigma_delta, nsigma=args.nsigma)
    print(f"Conservative bound: |C_mu| <= {cmax:.3e}  (at {args.nsigma:.1f}σ), using Δa_mu ≃ Re(C_mu).")

if __name__ == "__main__":
    main()
