#!/usr/bin/env python3
"""make_lambda1p4_vs_sigma_obsband.py

Generates the *data-based* Λ_1.4(σ) / ΔΛ_1.4(σ) main-text figure for SLy and AP4
with a quadratic fit and a Monte-Carlo (MC) uncertainty band.

Inputs (first found is used):
  - outputs/scan_grid.csv
  - outputs/headline_without_diagnostics.csv
  - outputs/headline_with_diagnostics.csv

Expected columns (flexible, case-insensitive):
  eos, sigma, Lambda_1p4 (or lambda_1p4), status (optional)

The script performs a per-EOS quadratic fit in σ and plots the fitted median.
It then builds a 5–95% envelope from an MC propagation with N samples
(--mc-samples, default 1000).

If the input provides explicit uncertainty columns (p5/p95), those are used as
per-σ spread estimates. Otherwise, the script falls back to a conservative
heuristic point scatter (5% relative + absolute floor) to avoid a degenerate band.

Outputs:
  - outputs/figures/lambda1p4_sigma_sly_ap4_quadratic_mc1000.png
  - outputs/figures/lambda1p4_sigma_sly_ap4_quadratic_mc1000.pdf
  - outputs/tables/lambda1p4_sigma_sly_ap4_quadratic_mc1000.csv

Observation overlay:
  An illustrative band is shaded for quick visual comparison.
  By default it uses Λ_1.4 ∈ [133, 686] (edit via CLI args).
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path
from typing import Optional, Tuple

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def _find_input() -> Path:
    candidates = [
        Path("outputs/deltaLambda_sigma_panel.csv"),
        Path("outputs/scan_grid.csv"),
        Path("outputs/headline_without_diagnostics.csv"),
        Path("outputs/headline_with_diagnostics.csv"),
    ]
    for p in candidates:
        if p.exists():
            return p
    raise FileNotFoundError(
        "No input CSV found. Provide one of outputs/scan_grid.csv, "
        "outputs/headline_without_diagnostics.csv, or outputs/headline_with_diagnostics.csv."
    )


def _col(df: pd.DataFrame, *names: str) -> Optional[str]:
    lower = {c.lower(): c for c in df.columns}
    for n in names:
        if n.lower() in lower:
            return lower[n.lower()]
    return None


def _as_numeric(s: pd.Series) -> pd.Series:
    return pd.to_numeric(s, errors="coerce")


def quadratic_fit(x: np.ndarray, y: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """Return coefficients (a,b,c) for y = a x^2 + b x + c and y_fit on x."""
    if len(x) < 3:
        # fall back to linear/constant
        if len(x) == 2:
            b, c = np.polyfit(x, y, 1)
            a = 0.0
        else:
            a, b, c = 0.0, 0.0, float(y[0]) if len(y) == 1 else 0.0
        y_fit = a * x * x + b * x + c
        return np.array([a, b, c]), y_fit
    coeff = np.polyfit(x, y, 2)
    y_fit = np.polyval(coeff, x)
    return coeff, y_fit


def mc_band_quadratic(
    x: np.ndarray,
    y: np.ndarray,
    y_sigma: np.ndarray,
    x_grid: np.ndarray,
    n: int,
    seed: int,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return (median, p5, p95) on x_grid from MC quadratic refits."""
    rng = np.random.default_rng(seed)
    preds = np.empty((n, len(x_grid)))
    for i in range(n):
        y_s = y + rng.normal(0.0, y_sigma)
        coef = np.polyfit(x, y_s, 2)
        preds[i] = np.polyval(coef, x_grid)
    return (
        np.percentile(preds, 50, axis=0),
        np.percentile(preds, 5, axis=0),
        np.percentile(preds, 95, axis=0),
    )


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--eos", nargs="+", default=["SLy", "AP4"], help="EOS names to include")
    ap.add_argument("--obs-min", type=float, default=133.0, help="Lower Λ_1.4 observational band (illustrative)")
    ap.add_argument("--obs-max", type=float, default=686.0, help="Upper Λ_1.4 observational band (illustrative)")
    ap.add_argument("--mc-samples", type=int, default=1000, help="MC samples for the uncertainty envelope")
    ap.add_argument("--rel-sigma", type=float, default=0.05, help="Fallback relative point scatter if no p5/p95")
    ap.add_argument("--abs-floor", type=float, default=1.0, help="Fallback absolute scatter floor if no p5/p95")
    ap.add_argument(
        "--out-prefix",
        default="outputs/figures/lambda1p4_sigma_sly_ap4_quadratic_mc1000",
        help="Output prefix",
    )
    args = ap.parse_args()

    inp = _find_input()
    df = pd.read_csv(inp)
    df.columns = [c.strip() for c in df.columns]

    eos_c = _col(df, "eos")
    sig_c = _col(df, "sigma")
    lam_c = _col(df, "Lambda_1p4", "lambda_1p4", "Lambda_1.4", "Lambda_1.4", "lambda")
    status_c = _col(df, "status")
    p5_c = _col(df, "Lambda_1p4_p5", "lambda_1p4_p5", "p5")
    p95_c = _col(df, "Lambda_1p4_p95", "lambda_1p4_p95", "p95")

    if eos_c is None or sig_c is None or lam_c is None:
        raise ValueError(
            f"Input CSV missing required columns. Found columns: {list(df.columns)}"
        )

    df = df.copy()
    df[sig_c] = _as_numeric(df[sig_c])
    df[lam_c] = _as_numeric(df[lam_c])
    if status_c is not None:
        # keep accepted if present
        keep = df[status_c].astype(str).str.lower().isin(["accepted", "done", "resolved", "stress_resolved"])
        # if no accepted-like statuses, keep all
        if keep.any():
            df = df[keep]

    out_dir = Path(args.out_prefix).parent
    out_dir.mkdir(parents=True, exist_ok=True)

    out_csv = Path("outputs/tables/lambda1p4_sigma_sly_ap4_quadratic_mc1000.csv")
    out_csv.parent.mkdir(parents=True, exist_ok=True)

    plt.figure(figsize=(6.8, 4.2))
    # illustrative obs band
    plt.axhspan(args.obs_min, args.obs_max, alpha=0.15)

    rows = []

    for eos in args.eos:
        eos_series = df[eos_c].astype(str)
        sub = df[eos_series == eos].dropna(subset=[sig_c, lam_c])
        if sub.empty:
            # fall back: substring match (useful if EOS labels include citations)
            sub = df[eos_series.str.contains(eos, case=False, na=False)].dropna(subset=[sig_c, lam_c])
        if sub.empty:
            continue
        # aggregate per sigma by median
        grp = sub.groupby(sig_c, as_index=False)[lam_c].median().sort_values(sig_c)
        x = grp[sig_c].to_numpy(dtype=float)
        y = grp[lam_c].to_numpy(dtype=float)

        # Identify GR baseline as sigma==0 (or nearest)
        idx0 = int(np.argmin(np.abs(x - 0.0)))
        lam0 = float(y[idx0])
        dlam = y - lam0

        # Quadratic fit (for plotting the median curve)
        coeff, _ = quadratic_fit(x, y)
        xg = np.linspace(x.min(), x.max(), 200)
        yg = np.polyval(coeff, xg)

        # Determine per-point sigma for MC (use p5/p95 if present; else fallback)
        if p5_c is not None and p95_c is not None and p5_c in sub.columns and p95_c in sub.columns:
            b = sub.groupby(sig_c, as_index=False)[[p5_c, p95_c]].median().sort_values(sig_c)
            y1 = _as_numeric(b[p5_c]).to_numpy(dtype=float)
            y2 = _as_numeric(b[p95_c]).to_numpy(dtype=float)
            y_sigma = 0.5 * (y2 - y1) / 1.645  # approx 1σ from 90% width
        else:
            y_sigma = np.abs(y) * float(args.rel_sigma) + float(args.abs_floor)

        # MC band on a dense sigma grid, performed on ΔΛ then shifted back
        x_band = np.linspace(x.min(), x.max(), 200)
        d_med, d_p5, d_p95 = mc_band_quadratic(
            x=x,
            y=dlam,
            y_sigma=y_sigma,
            x_grid=x_band,
            n=int(args.mc_samples),
            seed=12345 if eos.lower().startswith("sly") else 23456,
        )
        L_med = lam0 + d_med
        L_p5 = lam0 + d_p5
        L_p95 = lam0 + d_p95

        # plot points + median fit + MC envelope
        plt.plot(x, y, marker="o", linestyle="none", label=f"{eos} (run medians)")
        plt.plot(xg, yg, linestyle="-", linewidth=1.5, label=f"{eos} quadratic fit")
        plt.fill_between(x_band, L_p5, L_p95, alpha=0.18)

        # write CSV rows
        for xx, lmed, lp5, lp95, dmed, dp5, dp95 in zip(x_band, L_med, L_p5, L_p95, d_med, d_p5, d_p95):
            rows.append(
                {
                    "EOS": eos,
                    "sigma": float(xx),
                    "Lambda1p4_GR": lam0,
                    "Lambda1p4_median": float(lmed),
                    "Lambda1p4_p5": float(lp5),
                    "Lambda1p4_p95": float(lp95),
                    "DeltaLambda1p4_median": float(dmed),
                    "DeltaLambda1p4_p5": float(dp5),
                    "DeltaLambda1p4_p95": float(dp95),
                    "mc_samples": int(args.mc_samples),
                }
            )

    plt.xlabel(r"$\sigma$")
    plt.ylabel(r"$\Lambda_{1.4}$")
    plt.title(r"$\Lambda_{1.4}(\sigma)$ (SLy, AP4): quadratic fit + 1000-sample MC band")
    plt.legend(fontsize="small")
    plt.tight_layout()

    png = f"{args.out_prefix}.png"
    pdf = f"{args.out_prefix}.pdf"
    plt.savefig(png, dpi=300)
    plt.savefig(pdf)
    plt.close()

    if rows:
        pd.DataFrame(rows).to_csv(out_csv, index=False)
        print(f"Wrote: {out_csv}")

    print(f"Input: {inp}")
    print(f"Wrote: {png}")
    print(f"Wrote: {pdf}")


if __name__ == "__main__":
    main()
