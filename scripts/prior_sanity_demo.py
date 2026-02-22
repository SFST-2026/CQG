#!/usr/bin/env python3
"""
Prior-sanity demonstrator (toy example).

Creates an overlay plot of example priors on sigma and a synthetic posterior.
This is meant as a *template* illustrating how to report prior sensitivity.

Outputs:
- figures/prior_sanity_demo.pdf
"""
import argparse, os
import numpy as np
import matplotlib.pyplot as plt

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="figures")
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)

    x = np.linspace(-0.02, 0.12, 500)

    # Example priors (replace with your actual priors)
    prior_narrow = np.where((x>=0.00) & (x<=0.04), 1.0, 0.0)
    prior_wide   = np.where((x>=-0.01) & (x<=0.08), 1.0, 0.0)
    prior_narrow = prior_narrow / np.trapz(prior_narrow, x)
    prior_wide   = prior_wide / np.trapz(prior_wide, x)

    # Synthetic posterior example (replace with actual posterior KDE or histogram)
    mu, sig = 0.02, 0.01
    post = np.exp(-0.5*((x-mu)/sig)**2)
    post = post / np.trapz(post, x)

    plt.figure()
    plt.plot(x, prior_narrow, label="prior (narrow)")
    plt.plot(x, prior_wide, label="prior (wide)")
    plt.plot(x, post, label="posterior (example)")
    plt.xlabel(r"$\sigma$")
    plt.ylabel("density")
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(args.out, "prior_sanity_demo.pdf"))
    plt.close()

if __name__ == "__main__":
    main()
