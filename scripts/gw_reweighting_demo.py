#!/usr/bin/env python3
"""
GW reweighting demonstrator (toy example).

This script is intentionally *minimal* and uses a synthetic posterior sample file to show
the mechanics of reweighting under an alternative model. Replace the example posterior
with real GW posterior samples (e.g., from a public release) when performing an actual test.

Inputs (CSV):
- posterior_samples.csv: columns must include at least:
    event_id, m1, m2, Lambda14  (Lambda14 can be replaced by per-sample Lambda if available)

Outputs:
- figures/gw_reweighting_demo.pdf
- figures/gw_reweighting_demo_reweighted.csv

Usage:
    python scripts/gw_reweighting_demo.py --in data/examples_gw/posterior_samples.csv --out figures
"""
import argparse, os, json, time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def sfst_weight(Lambda14, sigma, sigma0=0.0, scale=200.0):
    """
    Toy weight model: prefers Lambda14 shifts of order sigma*scale.
    Replace this with a physically derived likelihood ratio when available.
    """
    target = Lambda14 + (sigma - sigma0) * scale
    # Broad Gaussian preference (toy)
    return np.exp(-0.5*((Lambda14 - target)/scale)**2)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", required=True)
    ap.add_argument("--out", dest="outdir", required=True)
    ap.add_argument("--sigma", type=float, default=0.02)
    args = ap.parse_args()

    os.makedirs(args.outdir, exist_ok=True)
    df = pd.read_csv(args.inp)
    if "Lambda14" not in df.columns:
        raise ValueError("Input must include column 'Lambda14'.")

    w = sfst_weight(df["Lambda14"].to_numpy(), sigma=args.sigma)
    w = w / np.mean(w)  # normalize for numerical stability

    # Resample (simple importance resampling)
    rng = np.random.default_rng(12345)
    idx = rng.choice(len(df), size=len(df), replace=True, p=w/w.sum())
    df_rw = df.iloc[idx].copy()
    df_rw["weight"] = w[idx]

    # Plot original vs reweighted Lambda14
    plt.figure()
    plt.hist(df["Lambda14"], bins=40, density=True, alpha=0.5, label="original")
    plt.hist(df_rw["Lambda14"], bins=40, density=True, alpha=0.5, label=f"reweighted (sigma={args.sigma:g})")
    plt.xlabel(r"$\Lambda_{1.4}$")
    plt.ylabel("density")
    plt.legend()
    plt.tight_layout()
    out_pdf = os.path.join(args.outdir, "gw_reweighting_demo.pdf")
    plt.savefig(out_pdf)
    plt.close()

    out_csv = os.path.join(args.outdir, "gw_reweighting_demo_reweighted.csv")
    df_rw.to_csv(out_csv, index=False)

    meta = {
        "created_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "input_file": args.inp,
        "output_pdf": out_pdf,
        "output_csv": out_csv,
        "sigma": args.sigma,
        "note": "Toy demonstrator only. Replace synthetic posterior with real GW posterior samples for any scientific claim."
    }
    with open(os.path.join(args.outdir, "gw_reweighting_demo_metadata.json"), "w") as f:
        json.dump(meta, f, indent=2)

if __name__ == "__main__":
    main()
