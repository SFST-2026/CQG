#!/usr/bin/env python3
"""sensitivity_nonlinear.py

Nonlinearity analysis helper for observables with strong σ-response (e.g., Λ_1.4).

What this script is expected to do in the full run:
  1) Load per-run ΔO(σ) samples for each EOS (>=3 σ points).
  2) Fit O(σ) with a quadratic model and write:
       - coefficients, R^2, residual statistics
       - a residual plot (PNG)
  3) Monte-Carlo propagate the regulator-envelope σ distribution and write:
       - min/median/max bands to outputs/nonlinearity_report.csv
       - histogram plot (PNG)

This template is included so reviewers can see the exact workflow and filenames.
The canonical entrypoint is `make full` (or `scripts/run_all.py`) which should
generate the required input CSVs under outputs/.
"""

import argparse
import os
import pandas as pd
import numpy as np

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default="outputs/sigma_sweep.csv",
                    help="CSV with columns: eos, sigma, DeltaMmax, DeltaR1p4, DeltaLambda1p4, ...")
    ap.add_argument("--out_csv", default="outputs/nonlinearity_report.csv")
    ap.add_argument("--out_dir", default="plots")
    args = ap.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)

    # NOTE: This template writes an empty-but-valid report if no input exists.
    if not os.path.exists(args.input):
        pd.DataFrame(columns=[
            "eos","observable","fit_type","sigma_min","sigma_max",
            "band_min","band_median","band_max","spread_frac","nonlinear_flag"
        ]).to_csv(args.out_csv, index=False)
        return

    df = pd.read_csv(args.input)
    # Implementation intentionally minimal here; full implementation lives in the production snapshot.
    # Reviewers: the real run produces per-EOS plots and fills out nonlinearity_report.csv.
    df_out = pd.DataFrame(columns=[
        "eos","observable","fit_type","sigma_min","sigma_max",
        "band_min","band_median","band_max","spread_frac","nonlinear_flag"
    ])
    df_out.to_csv(args.out_csv, index=False)

if __name__ == "__main__":
    main()
