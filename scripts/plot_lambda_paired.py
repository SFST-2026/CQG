#!/usr/bin/env python3
"""
Create the paired Λ1.4 figure showing robustness to DIAGNOSTIC/EXCLUDED exclusions.

Outputs:
  figures/lambda1p4_paired_including_excluding_clipped.png
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

INP = Path("outputs/lambda_nonlinearity_summary.csv")
OUT = Path("figures/lambda1p4_paired_including_excluding_clipped.png")

def main() -> None:
    df = pd.read_csv(INP).sort_values("EOS")
    labels = list(df["EOS"])
    x = np.arange(len(labels))

    inc = df
    exc = df[df["status"] == "accepted"]

    def series(d, col):
        m = dict(zip(d["EOS"], d[col]))
        return np.array([m.get(l, np.nan) for l in labels], dtype=float)

    inc_med = series(inc, "mc_med")
    inc_5 = series(inc, "mc_5")
    inc_95 = series(inc, "mc_95")

    exc_med = series(exc, "mc_med")
    exc_5 = series(exc, "mc_5")
    exc_95 = series(exc, "mc_95")

    # Limits based on the accepted set (so diagnostics do not blow up the y-scale).
    finite = np.isfinite(exc_med)
    vals = np.concatenate([exc_5[finite], exc_95[finite], exc_med[finite]])
    ymin, ymax = float(np.min(vals)), float(np.max(vals))
    pad = 0.2 * (ymax - ymin if ymax > ymin else 1.0)
    ylo, yhi = ymin - pad, ymax + pad

    OUT.parent.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(10, 5))

    # Excluding diagnostics: band + markers
    ax.fill_between(x[finite], exc_5[finite], exc_95[finite], alpha=0.25,
                    label="MC 5–95% (excluding DIAGNOSTIC/EXCLUDED)")
    ax.plot(x[finite], exc_med[finite], marker="o", label="MC median (excluding)")

    # Including all: dashed median (and optional band)
    ax.plot(x, inc_med, linestyle="--", marker="x", label="MC median (including all)")

    # Mark outliers beyond the displayed y-range
    for xi, y in zip(x, inc_med):
        if np.isfinite(y) and (y < ylo or y > yhi):
            ax.annotate("outlier", (xi, np.clip(y, ylo, yhi)), textcoords="offset points",
                        xytext=(0, 10), ha="center", fontsize=8)

    ax.set_ylim(ylo, yhi)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=45, ha="right")
    ax.set_ylabel("ΔΛ1.4 [%] at σ=0.06")
    ax.set_title("Paired Λ1.4 headline: excluding vs including diagnostics")
    ax.legend()
    fig.tight_layout()
    fig.savefig(OUT, dpi=300)
    print(f"Wrote {OUT}")

if __name__ == "__main__":
    main()
