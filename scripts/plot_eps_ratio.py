#!/usr/bin/env python3
"""plot_eps_ratio.py

I generate the physical plausibility diagnostic plot:
  eps_vac_inertial(r) / eps_ref(r)  vs radius r

Inputs (CSV):
  - profile CSV with columns: r, eps_ref, eps_vac_inertial   (names configurable)

Outputs:
  - plots/epsratio_<EOS>_<case>.png
  - outputs/epsratio_summary.csv with absmax per run (for validate_run.py gate)

This script is intentionally lightweight and reviewer-friendly.
"""

import argparse
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--profile", required=True, help="Profile CSV path")
    ap.add_argument("--eos", default="EOS", help="EOS label for filename")
    ap.add_argument("--case", default="case", help="Case tag for filename")
    ap.add_argument("--rcol", default="r")
    ap.add_argument("--eref", default="eps_ref")
    ap.add_argument("--evac", default="eps_vac_inertial")
    ap.add_argument("--outdir", default="plots")
    ap.add_argument("--summary", default="outputs/epsratio_summary.csv")
    args = ap.parse_args()

    df = pd.read_csv(args.profile)
    r = df[args.rcol].to_numpy()
    eref = df[args.eref].to_numpy()
    evac = df[args.evac].to_numpy()

    ratio = evac / np.maximum(1e-300, eref)
    absmax = float(np.max(np.abs(ratio)))

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    figpath = outdir / f"epsratio_{args.eos}_{args.case}.png"

    plt.figure(figsize=(7,4))
    plt.plot(r, ratio)
    plt.xlabel("r")
    plt.ylabel(r"$\epsilon_{\mathrm{vac,inertial}}/\epsilon_{\mathrm{ref}}$")
    plt.title(f"eps_vac,inertial / eps_ref (absmax={absmax:.3g})")
    plt.grid(True, ls=":", alpha=0.6)
    plt.tight_layout()
    plt.savefig(figpath, dpi=200)
    plt.close()

    # append summary row
    summ_path = Path(args.summary)
    summ_path.parent.mkdir(parents=True, exist_ok=True)
    row = pd.DataFrame([{"eos": args.eos, "case_tag": args.case, "epsratio_absmax": absmax, "plot": str(figpath)}])
    if summ_path.exists():
        old = pd.read_csv(summ_path)
        out = pd.concat([old, row], ignore_index=True)
    else:
        out = row
    out.to_csv(summ_path, index=False)

    print(f"Wrote {figpath} and updated {summ_path}")


if __name__ == "__main__":
    main()
