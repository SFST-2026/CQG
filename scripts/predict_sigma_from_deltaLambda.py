#!/usr/bin/env python3
"""
Compute sigma_req from an observed DeltaLambda_obs using archived SFST sensitivities.

Usage:
  python scripts/predict_sigma_from_deltaLambda.py --eos "AP4-PP(Read2009)" --deltaLambda -50

Outputs:
  sigma_req estimate and gate status based on epsratio proxy thresholds.

Notes:
  This snapshot contains σ=0 and σ=0.06 points; S_Lambda is computed from those.
"""
import argparse, os
import pandas as pd
import numpy as np

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--eos", required=True, help="EOS label as in outputs/scan_summary.csv")
    ap.add_argument("--deltaLambda", type=float, required=True, help="Observed DeltaLambda (absolute)")
    ap.add_argument("--sigma_ref", type=float, default=0.06, help="Reference sigma point in snapshot (default 0.06)")
    args=ap.parse_args()

    root=os.path.abspath(os.path.join(os.path.dirname(__file__),".."))
    scan=pd.read_csv(os.path.join(root,"outputs","scan_summary.csv"))

    base=scan[(scan["EOS"]==args.eos) & (scan["sigma"]==0)].iloc[0]
    ref =scan[(scan["EOS"]==args.eos) & (scan["sigma"]==args.sigma_ref) & (scan["case"]=="C_sigma_chi")].iloc[0]

    delta_abs = base["Lambda_1.4"] * (ref["Delta_Lambda14_pct"]/100.0)
    S = delta_abs / args.sigma_ref

    sigma_req = args.deltaLambda / S if S!=0 else np.nan

    gate = "ACCEPTED" if abs(sigma_req) <= 0.10 else ("STRESS" if abs(sigma_req) <= 0.30 else "DIAGNOSTIC")
    print(f"EOS: {args.eos}")
    print(f"Baseline Λ1.4: {base['Lambda_1.4']:.3f}")
    print(f"At σ={args.sigma_ref}: ΔΛ ≈ {delta_abs:.3f}  => S_Λ ≈ {S:.3f} per σ")
    print(f"Input ΔΛ_obs: {args.deltaLambda:.3f}")
    print(f"σ_req ≈ {sigma_req:.4f}")
    print(f"Gate (proxy): {gate} (thresholds: 0.10 / 0.30)")

if __name__=="__main__":
    main()
