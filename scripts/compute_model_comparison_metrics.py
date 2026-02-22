#!/usr/bin/env python3
"""Compute lightweight model-comparison metrics from posterior samples.

This is intentionally minimal and reviewer-facing:
- 1D posterior overlap for a chosen observable
- Optional Δmean/Δmedian and a simple effect size

Inputs:
- CSV with at least: model, eos, observable, value
  where model in {"SM","SFST"}

Outputs:
- CSV summary with overlap + basic stats per (eos, observable)

Example:
  python scripts/compute_model_comparison_metrics.py \
    --in data/examples_sensitivity/posterior_samples.csv \
    --out outputs/model_compare_metrics.csv \
    --observable R14
"""

import argparse
import json
import numpy as np
import pandas as pd


def kde_overlap(x, y, bins=200):
    """Histogram-based overlap (fast, no scipy dependency)."""
    lo = min(np.min(x), np.min(y))
    hi = max(np.max(x), np.max(y))
    if not np.isfinite(lo) or not np.isfinite(hi) or lo == hi:
        return np.nan
    hx, edges = np.histogram(x, bins=bins, range=(lo, hi), density=True)
    hy, _ = np.histogram(y, bins=bins, range=(lo, hi), density=True)
    dx = edges[1] - edges[0]
    return float(np.sum(np.minimum(hx, hy)) * dx)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", required=True)
    ap.add_argument("--out", dest="out", required=True)
    ap.add_argument("--observable", default=None, help="Filter to a single observable name")
    ap.add_argument("--meta", default=None, help="Optional plot_metadata/provenance JSON to embed")
    args = ap.parse_args()

    df = pd.read_csv(args.inp)
    required = {"model", "eos", "observable", "value"}
    missing = required - set(df.columns)
    if missing:
        raise SystemExit(f"Missing required columns: {sorted(missing)}")

    if args.observable:
        df = df[df["observable"] == args.observable]

    out_rows = []
    for (eos, obs), g in df.groupby(["eos", "observable"]):
        sm = g[g["model"] == "SM"]["value"].to_numpy()
        sf = g[g["model"] == "SFST"]["value"].to_numpy()
        if len(sm) < 50 or len(sf) < 50:
            overlap = np.nan
        else:
            overlap = kde_overlap(sm, sf)

        out_rows.append({
            "eos": eos,
            "observable": obs,
            "n_sm": int(len(sm)),
            "n_sfst": int(len(sf)),
            "overlap_1d": overlap,
            "mean_sm": float(np.mean(sm)) if len(sm) else np.nan,
            "mean_sfst": float(np.mean(sf)) if len(sf) else np.nan,
            "delta_mean": float(np.mean(sf) - np.mean(sm)) if len(sm) and len(sf) else np.nan,
            "median_sm": float(np.median(sm)) if len(sm) else np.nan,
            "median_sfst": float(np.median(sf)) if len(sf) else np.nan,
            "delta_median": float(np.median(sf) - np.median(sm)) if len(sm) and len(sf) else np.nan,
        })

    out_df = pd.DataFrame(out_rows).sort_values(["eos", "observable"])
    out_df.to_csv(args.out, index=False)

    if args.meta:
        try:
            with open(args.meta, "r", encoding="utf-8") as f:
                meta = json.load(f)
            meta_out = args.out.replace(".csv", ".meta.json")
            with open(meta_out, "w", encoding="utf-8") as f:
                json.dump(meta, f, indent=2)
        except Exception as e:
            print(f"Warning: could not write meta sidecar: {e}")


if __name__ == "__main__":
    main()
