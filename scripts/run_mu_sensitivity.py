import os
import sys

# Ensure repo root is importable when this script is executed as a file.
_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from pathlib import Path
import pandas as pd
import numpy as np

def main():
    scan = pd.read_csv("outputs/regulator_scan/sigma_pp_scan.csv")
    d = scan[scan["scheme"]=="DimReg_finite"].copy()
    if d.empty:
        raise RuntimeError("No DimReg_finite rows found in sigma_pp_scan.csv")
    d = d.sort_values("scale")
    mu0 = 1.0
    scales = d["scale"].to_numpy()
    sig = d["Sigma_pp"].to_numpy()
    i0 = int(np.argmin(np.abs(scales-mu0)))
    if i0==0 or i0==len(scales)-1:
        raise RuntimeError("Need mu scan on both sides of mu0 to compute derivative")
    mu_minus, mu_plus = scales[i0-1], scales[i0+1]
    s_minus, s_plus = sig[i0-1], sig[i0+1]
    dSigma_dlnmu = (s_plus - s_minus) / (np.log(mu_plus) - np.log(mu_minus))
    out = pd.DataFrame([{
        "mu_minus": mu_minus,
        "mu0": scales[i0],
        "mu_plus": mu_plus,
        "Sigma_pp(mu_minus)": s_minus,
        "Sigma_pp(mu0)": sig[i0],
        "Sigma_pp(mu_plus)": s_plus,
        "dSigma_pp_dlnmu": dSigma_dlnmu
    }])
    outdir = Path("outputs/renorm")
    outdir.mkdir(parents=True, exist_ok=True)
    out.to_csv(outdir/"mu_derivative.csv", index=False)
    print(out)
    print("Wrote outputs/renorm/mu_derivative.csv")

if __name__ == "__main__":
    main()
