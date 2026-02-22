import os
import sys

# Ensure repo root is importable when this script is executed as a file.
_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from pathlib import Path
import pandas as pd
import numpy as np
from sfst_qfis_repro import make_piecewise_eos, scan_eos

def interp(x, xp, fp):
    return float(np.interp(x, xp, fp))

def summarize(df: pd.DataFrame, target_mass=1.4):
    M = df["M_msun"].to_numpy()
    R = df["R_km"].to_numpy()
    L = df["Lambda"].to_numpy()
    i = int(np.nanargmax(M))
    Mmax = float(M[i]); R_Mmax=float(R[i]); L_Mmax=float(L[i])
    order = np.argsort(M)
    M_s = M[order]; R_s=R[order]; L_s=L[order]
    if M_s.min()<=target_mass<=M_s.max():
        R14 = interp(target_mass, M_s, R_s)
        L14 = interp(target_mass, M_s, L_s)
    else:
        R14=float("nan"); L14=float("nan")
    return {"Mmax":Mmax,"R_Mmax_km":R_Mmax,"Lambda_Mmax":L_Mmax,"R_1.4_km":R14,"Lambda_1.4":L14}

if __name__ == "__main__":
    outdir = Path("outputs/variant_AB")
    outdir.mkdir(parents=True, exist_ok=True)

    eos_list = [
        make_piecewise_eos(34.384, 3.005, 2.988, 2.851, "SLy-PP(Read2009)"),
        make_piecewise_eos(34.269, 2.830, 3.445, 3.348, "AP4-PP(Read2009)"),
    ]

    rows=[]
    for eos in eos_list:
        for include_in_gravity in [False, True]:
            df = scan_eos(eos, sigma_vac=0.06, chi_vac=1.0, screening_factor=1.0, include_in_gravity=include_in_gravity)
            df.to_csv(outdir/f"{eos.name}_sigma0p06_grav{include_in_gravity}.csv", index=False)
            s = summarize(df)
            s.update({"EOS":eos.name,"sigma":0.06,"chi":1.0,"include_in_gravity":include_in_gravity})
            rows.append(s)

    comp = pd.DataFrame(rows)
    comp.to_csv(outdir/"variantA_vs_B_summary.csv", index=False)
    print(comp)
