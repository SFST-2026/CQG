#!/usr/bin/env python3
"""Regulator/matching sensitivity demo (bounded).

Reads a CSV with Lambda1.4 vs sigma for multiple regulator settings and
produces a band plot plus a small summary table.

Default input is a synthetic example. Replace with real scan outputs.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", default="data/examples_sensitivity/regulator_lambda1p4_band.csv",
                    help="CSV with columns: regulator_id,sigma,lambda14")
    ap.add_argument("--out-fig-dir", default="figures")
    ap.add_argument("--out-table", default="supplement/tables/regulator_sensitivity_summary.csv")
    args = ap.parse_args()

    csv_path = Path(args.csv)
    out_fig_dir = Path(args.out_fig_dir)
    out_fig_dir.mkdir(parents=True, exist_ok=True)
    out_table = Path(args.out_table)
    out_table.parent.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(csv_path, comment="#", header=None)
    if df.shape[1] == 3:
        df.columns = ["regulator_id", "sigma", "lambda14"]
    else:
        df = pd.read_csv(csv_path, comment="#")
        df = df[["regulator_id", "sigma", "lambda14"]]

    df["sigma"] = df["sigma"].astype(float)
    df["lambda14"] = df["lambda14"].astype(float)

    # Compute envelope across regulators at each sigma
    env = df.groupby("sigma")["lambda14"].agg(["min", "max", "median"]).reset_index()
    env.to_csv(out_table, index=False)

    plt.figure()
    # Plot individual regulators lightly
    for rid, g in df.groupby("regulator_id"):
        g = g.sort_values("sigma")
        plt.plot(g["sigma"], g["lambda14"], marker="o", linewidth=1, alpha=0.6)

    # Plot envelope band
    env = env.sort_values("sigma")
    plt.fill_between(env["sigma"], env["min"], env["max"], alpha=0.2, label="envelope")
    plt.plot(env["sigma"], env["median"], linewidth=2, label="median")

    plt.xlabel("sigma")
    plt.ylabel("Lambda_1.4")
    plt.legend()
    plt.tight_layout()

    plt.savefig(out_fig_dir / "regulator_sensitivity_band.pdf")
    plt.savefig(out_fig_dir / "regulator_sensitivity_band.png", dpi=600)


if __name__ == "__main__":
    main()
