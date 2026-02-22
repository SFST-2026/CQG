#!/usr/bin/env python3
"""Minimal, reproducible GW170817-style reweighting demonstrator.

This is intentionally lightweight: it loads a posterior sample over Lambda_1.4
(or a proxy), applies a user-defined SFST mapping Lambda_1.4(sigma), and
computes reweighted summary statistics.

Default input is a small *synthetic* CSV template shipped with the repo.
For a real analysis, replace the input CSV with public posterior samples.

Outputs:
- supplement/tables/gw170817_reweight_summary.csv
"""

from __future__ import annotations

import argparse
from pathlib import Path
import numpy as np
import pandas as pd


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--posterior", default="data/examples_gw/gw170817_like_posterior.csv",
                    help="CSV with columns: lambda14,weight")
    ap.add_argument("--sigma", type=float, default=0.04, help="Example sigma value")
    ap.add_argument("--out", default="supplement/tables/gw170817_reweight_summary.csv")
    args = ap.parse_args()

    df = pd.read_csv(args.posterior, comment="#", header=None)
    if df.shape[1] == 2:
        df.columns = ["lambda14", "weight"]
    else:
        df = pd.read_csv(args.posterior, comment="#")
        df = df[["lambda14", "weight"]]

    lam = df["lambda14"].astype(float).to_numpy()
    w = df["weight"].astype(float).to_numpy()
    w = w / np.sum(w)

    # Minimal SFST mapping (placeholder): Lambda shifts by a factor depending on sigma.
    # Replace with the paper's computed Lambda_1.4(sigma) relation.
    # Here we apply a small multiplicative shift for demonstration.
    lam_sfst = lam * (1.0 + 0.8 * args.sigma)

    # Reweighting example: assume likelihood prefers lam_sfst close to the original lam
    # (this is only a *demonstrator*). Replace with real likelihood / model evidence.
    # We use a Gaussian penalty on the shift magnitude.
    delta = lam_sfst - lam
    scale = np.std(lam) if np.std(lam) > 0 else 1.0
    like = np.exp(-0.5 * (delta / (0.5 * scale)) ** 2)

    w_new = w * like
    w_new = w_new / np.sum(w_new)

    def wstats(x: np.ndarray, ww: np.ndarray) -> dict:
        mean = float(np.sum(x * ww))
        # weighted quantiles
        order = np.argsort(x)
        x2, ww2 = x[order], ww[order]
        cdf = np.cumsum(ww2)
        q10 = float(np.interp(0.10, cdf, x2))
        q50 = float(np.interp(0.50, cdf, x2))
        q90 = float(np.interp(0.90, cdf, x2))
        return {"mean": mean, "q10": q10, "q50": q50, "q90": q90}

    base = wstats(lam, w)
    after = wstats(lam_sfst, w_new)

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame([
        {"stage": "baseline", **base},
        {"stage": "reweighted_SFST_demo", **after, "sigma": args.sigma}
    ]).to_csv(out, index=False)


if __name__ == "__main__":
    main()
