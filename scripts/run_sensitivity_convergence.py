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

if __name__ == "__main__":
    outdir = Path("outputs/sensitivity_convergence")
    outdir.mkdir(parents=True, exist_ok=True)

    eos_list = [
        make_piecewise_eos(34.384, 3.005, 2.988, 2.851, "SLy-PP(Read2009)"),
        make_piecewise_eos(34.269, 2.830, 3.445, 3.348, "AP4-PP(Read2009)"),
    ]
    deltas=[0.02,0.04,0.06]
    rows=[]
    for eos in eos_list:
        df0=scan_eos(eos, sigma_vac=0.0, chi_vac=1.0, screening_factor=1.0, include_in_gravity=False)
        M0=df0["M_msun"].to_numpy(); 
        i0=int(np.nanargmax(M0)); M0max=float(M0[i0])
        order0=np.argsort(M0); M0s=M0[order0]
        R0s=df0["R_km"].to_numpy()[order0]; L0s=df0["Lambda"].to_numpy()[order0]
        R0=interp(1.4,M0s,R0s); L0=interp(1.4,M0s,L0s)
        for d in deltas:
            df=scan_eos(eos, sigma_vac=d, chi_vac=1.0, screening_factor=1.0, include_in_gravity=False)
            M=df["M_msun"].to_numpy(); i=int(np.nanargmax(M)); Mmax=float(M[i])
            order=np.argsort(M); Ms=M[order]
            Rs=df["R_km"].to_numpy()[order]; Ls=df["Lambda"].to_numpy()[order]
            R=interp(1.4,Ms,Rs); L=interp(1.4,Ms,Ls)
            rows.append({"EOS":eos.name,"delta_sigma":d,
                         "S_Mmax":(Mmax-M0max)/d,
                         "S_R1.4":(R-R0)/d,
                         "S_Lambda1.4":(L-L0)/d})
    conv=pd.DataFrame(rows)
    conv.to_csv(outdir/"sensitivity_convergence.csv", index=False)
    print(conv)
