#!/usr/bin/env python3
"""EOS spread sanity check (minimal).

This script produces an overlay of Lambda1.4 vs sigma for multiple EOS baselines.
It is designed to be *reproducible and lightweight* for reviewers.

Default input is a small synthetic example CSV. Replace the input path with
real outputs once available.

Outputs:
- figures/eos_sensitivity_overlay.pdf/png
- supplement/tables/eos_sensitivity_summary.csv
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", default="data/examples_sensitivity/eos_lambda1p4_vs_sigma.csv",
                    help="CSV with columns: eos,sigma,lambda14")
    ap.add_argument("--out-fig-dir", default="figures", help="Output figure directory")
    ap.add_argument("--out-table", default="supplement/tables/eos_sensitivity_summary.csv",
                    help="Output summary table path")
    args = ap.parse_args()

    csv_path = Path(args.csv)
    out_fig_dir = Path(args.out_fig_dir)
    out_fig_dir.mkdir(parents=True, exist_ok=True)
    out_table = Path(args.out_table)
    out_table.parent.mkdir(parents=True, exist_ok=True)

    # Read CSV, allow comment lines starting with '#'
    df = pd.read_csv(csv_path, comment="#", header=None)
    if df.shape[1] == 3:
        df.columns = ["eos", "sigma", "lambda14"]
    else:
        df = pd.read_csv(csv_path, comment="#")
        df = df[["eos", "sigma", "lambda14"]]

    df["sigma"] = df["sigma"].astype(float)
    df["lambda14"] = df["lambda14"].astype(float)

    # Summary table (per EOS): baseline, max shift, fractional shift
    summary = []
    for eos, g in df.groupby("eos"):
        g = g.sort_values("sigma")
        base = float(g.iloc[0]["lambda14"])
        maxv = float(g["lambda14"].max())
        minv = float(g["lambda14"].min())
        summary.append({
            "eos": eos,
            "lambda14_baseline": base,
            "lambda14_min": minv,
            "lambda14_max": maxv,
            "delta_lambda14_max": maxv - base,
            "delta_lambda14_max_frac": (maxv - base) / base if base != 0 else float("nan"),
        })
    pd.DataFrame(summary).to_csv(out_table, index=False)

    # Plot
    plt.figure()
    for eos, g in df.groupby("eos"):
        g = g.sort_values("sigma")
        plt.plot(g["sigma"].values, g["lambda14"].values, marker="o", label=eos)

    plt.xlabel("sigma")
    plt.ylabel("Lambda_1.4")
    plt.legend()
    plt.tight_layout()

    plt.savefig(out_fig_dir / "eos_sensitivity_overlay.pdf")
    plt.savefig(out_fig_dir / "eos_sensitivity_overlay.png", dpi=600)


if __name__ == "__main__":
    main()
