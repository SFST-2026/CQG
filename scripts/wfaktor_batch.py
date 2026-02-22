#!/usr/bin/env python3
"""Batch WFaktor computation.

I scan `outputs/diagnostics/**/` for `baseline_profile.csv` and `inserted_profile.csv`
and compute WFaktor_max for a chosen internal variable column.

This script is designed to be safe: if a case lacks the needed files, I skip it and
record the reason in the output table.
"""
import argparse
from pathlib import Path

import numpy as np
import pandas as pd

def compute_wfaktor(base: pd.DataFrame, ins: pd.DataFrame, var: str, rcol: str, eps: float):
    if var not in base.columns or var not in ins.columns:
        raise KeyError(f"missing column {var}")
    if rcol not in base.columns:
        raise KeyError(f"missing radius column {rcol}")
    Xb = base[var].to_numpy()
    Xs = ins[var].to_numpy()
    r = base[rcol].to_numpy()
    if Xb.shape != Xs.shape:
        raise ValueError("baseline and inserted arrays have different shapes/grids")
    denom = np.maximum(eps, np.abs(Xb))
    wf = np.abs(Xs - Xb) / denom
    i = int(np.argmax(wf))
    return float(np.max(wf)), float(r[i])

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default="outputs/diagnostics", help="diagnostics root")
    ap.add_argument("--internal-var", default="X_var", help="internal variable column name")
    ap.add_argument("--radius-col", default="r", help="radius column name")
    ap.add_argument("--eps-floor", type=float, default=1e-16)
    ap.add_argument("--out", default="outputs/wfaktor_summary.csv")
    args = ap.parse_args()

    root = Path(args.root)
    rows = []
    for case in sorted(root.glob("*")):
        if not case.is_dir():
            continue
        base_csv = case / "baseline_profile.csv"
        ins_csv  = case / "inserted_profile.csv"
        if not base_csv.exists() or not ins_csv.exists():
            rows.append({"case": case.name, "WFaktor_max": "", "r_max": "", "status": "skipped (missing profiles)"})
            continue
        try:
            base = pd.read_csv(base_csv)
            ins  = pd.read_csv(ins_csv)
            wfmax, rmax = compute_wfaktor(base, ins, args.internal_var, args.radius_col, args.eps_floor)
            rows.append({"case": case.name, "WFaktor_max": wfmax, "r_max": rmax, "status": "ok"})
        except Exception as e:
            rows.append({"case": case.name, "WFaktor_max": "", "r_max": "", "status": f"error: {e}"})

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(out, index=False)
    print(f"Wrote {out} with {len(rows)} rows")

if __name__ == "__main__":
    main()
