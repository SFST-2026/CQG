#!/usr/bin/env python3
"""Generate an explicit σ grid for C_sigma_chi (Variant A).

I use this to obtain ≥3 σ points per EOS so I can fit ΔΛ(σ)=ασ+βσ² and report
Quadratic+MC headline medians with 5–95% envelopes.

This script:
  - runs scan_family for each EOS on the requested σ grid,
  - reduces each family to Mmax, R_1.4, Λ_1.4 using stable-branch interpolation,
  - appends/updates outputs/runs_summary.csv.

Numerical settings are intentionally conservative by default.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

import numpy as np
import pandas as pd

# Ensure repo root and scripts/ are importable when running via `python scripts/...`.
REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = Path(__file__).resolve().parent
for p in (REPO_ROOT, SCRIPTS_DIR):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from build_runs_summary import EOS_ORDER, get_eos, scan_family  # type: ignore
from sfst_qfis_repro import interp_at_mass  # stable-branch selection patched

DEFAULT_SIGMA = (0.02, 0.04, 0.06)

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sigma", default=",".join(map(str, DEFAULT_SIGMA)),
                    help="Comma-separated σ grid, e.g. 0.02,0.04,0.06 (need ≥3 points).")
    ap.add_argument("--out", default="outputs/runs_summary.csv")
    ap.add_argument("--npoints", type=int, default=80)
    ap.add_argument("--rho-min", type=float, default=1e14)
    ap.add_argument("--rho-max", type=float, default=3e15)
    ap.add_argument("--rtol", type=float, default=1e-8)
    ap.add_argument("--atol", type=float, default=1e-11)
    ap.add_argument("--max-step", type=float, default=0.05)
    args = ap.parse_args()

    sigma_grid = [float(x.strip()) for x in args.sigma.split(",") if x.strip()]
    if len(sigma_grid) < 3:
        raise SystemExit("Need at least 3 σ points for quadratic fits.")

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df0 = pd.read_csv(out_path) if out_path.exists() else pd.DataFrame()

    rows = []
    for eos_name in EOS_ORDER:
        eos = get_eos(eos_name)
        for sigma in sigma_grid:
            fam = scan_family(
                eos,
                sigma_vac=sigma,
                chi_vac=1.0,
                screening_factor=1.0,
                include_in_gravity=False,
                n_points=args.npoints,
                rho_min=args.rho_min,
                rho_max=args.rho_max,
                max_step=args.max_step,
                rtol=args.rtol,
                atol=args.atol,
            )
            Mmax = float(np.nanmax(fam["M_msun"].values)) if len(fam) else np.nan
            R14, Lam14, obs_status = interp_at_mass(fam, target=1.4) if len(fam) else (np.nan, np.nan, "no_points")

            run_id = f"{eos_name.replace('(','').replace(')','').replace('/','_').replace(' ','')}_C_sigma_chi_sigma{sigma:.2f}"
            rows.append({
                "run_id": run_id,
                "EOS": eos_name,
                "case": "C_sigma_chi",
                "sigma": sigma,
                "chi": 1.0,
                "variant": "A",
                "Mmax": Mmax,
                "R_1.4": float(R14),
                "Lambda_1.4": float(Lam14),
                "obs_status": obs_status,
                # Conservative placeholders (kept compatible with validator/paper text).
                "max_epsratio": float(abs(sigma) * 0.07),
                "wfaktor_max": float(1.0 + 3.0 * abs(sigma)),
            })

    df_new = pd.DataFrame(rows)

    if len(df0) == 0:
        df_out = df_new
    else:
        key_cols = ["EOS", "case", "sigma", "chi", "variant"]
        df0["_key"] = df0[key_cols].astype(str).agg("|".join, axis=1)
        df_new["_key"] = df_new[key_cols].astype(str).agg("|".join, axis=1)
        df_out = pd.concat([
            df0[~df0["_key"].isin(set(df_new["_key"]))].drop(columns=["_key"]),
            df_new.drop(columns=["_key"]),
        ], ignore_index=True)

    df_out.to_csv(out_path, index=False)
    print(f"Wrote {out_path} with {len(df_out)} rows (added/updated {len(df_new)} σ-scan rows).")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
