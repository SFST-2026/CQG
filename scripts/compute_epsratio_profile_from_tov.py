#!/usr/bin/env python3
"""Compute epsratio(r) profile from a radial TOV profile dump.

This repository ships with *placeholder* epsratio profiles for reviewer-facing
numerical diagnostics. To obtain *physical* epsratio(r) curves you need a radial
profile dump from your actual TOV integrator.

Expected input CSV (tov_profile.csv):
  - r_km                : radius coordinate in km
  - eps_ref             : reference energy density used for normalization
  - eps_vac_inertial    : vacuum-induced inertial energy density (Variant A)

Output:
  - epsratio_profile.csv : columns [r_km, r_over_R, epsratio]
  - epsratio_profile.png : quick-look plot

Usage:
  python scripts/compute_epsratio_profile_from_tov.py \
    --in outputs/diagnostics/<run_id>/tov_profile.csv \
    --outdir outputs/diagnostics/<run_id>
"""

from __future__ import annotations

import argparse
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--in', dest='inp', required=True, help='Input tov_profile.csv path')
    ap.add_argument('--outdir', required=True, help='Output directory (diagnostics run dir)')
    ap.add_argument('--eps', type=float, default=1e-30, help='Small floor to avoid divide-by-zero')
    args = ap.parse_args()

    inp = Path(args.inp)
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(inp)
    required = {'r_km', 'eps_ref', 'eps_vac_inertial'}
    missing = required - set(df.columns)
    if missing:
        raise SystemExit(f"Missing columns in {inp}: {sorted(missing)}")

    r_km = df['r_km'].to_numpy(dtype=float)
    eps_ref = df['eps_ref'].to_numpy(dtype=float)
    eps_vac = df['eps_vac_inertial'].to_numpy(dtype=float)

    denom = np.maximum(np.abs(eps_ref), args.eps)
    epsratio = np.abs(eps_vac) / denom

    R_km = float(np.max(r_km)) if np.max(r_km) > 0 else 1.0
    r_over_R = r_km / R_km

    out = pd.DataFrame({'r_km': r_km, 'r_over_R': r_over_R, 'epsratio': epsratio})
    out_csv = outdir / 'epsratio_profile.csv'
    out.to_csv(out_csv, index=False)

    # Plot
    plt.figure(figsize=(8, 5))
    plt.plot(r_over_R, epsratio)
    plt.xlabel('r/R')
    plt.ylabel('epsratio')
    plt.title(f'epsratio profile (max={np.max(epsratio):.3g})')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(outdir / 'epsratio_profile.png', dpi=150)
    plt.close()

    print(f"Wrote {out_csv} and epsratio_profile.png")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
