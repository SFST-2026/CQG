import os
import sys

# Ensure repo root is importable when this script is executed as a file.
_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import integrate
from pathlib import Path

# Minimal example from the manuscript: I = (1/2π^2)∫ k^2/(k^2+m^2)^{3/2} dk is UV-divergent; PV makes it finite.
def integrand(k, m):
    return (k**2) / (k**2 + m**2)**1.5

def I_PV(M, m=1.0):
    pref = 1.0/(2.0*np.pi**2)
    f = lambda k: integrand(k, m) - integrand(k, M)
    val, err = integrate.quad(f, 0, np.inf, limit=200, epsabs=1e-11, epsrel=1e-11)
    return pref*val, err

def I_dimreg_finite(mu, m=1.0):
    # finite part only, scheme constant set to zero; see manuscript appendix.
    return (1.0/(2.0*np.pi**2))*np.log(mu/m)

if __name__ == "__main__":
    outdir = Path("outputs/regulator_scan")
    outdir.mkdir(parents=True, exist_ok=True)

    m = 1.0
    g = 1.0
    Ms = [10.0, 30.0, 100.0, 300.0, 1000.0]
    rows=[]
    for M in Ms:
        I, err = I_PV(M, m=m)
        Sigma_pp = g**2 * I
        rows.append({"scheme":"PV", "scale":M, "I":I, "I_err":err, "Sigma_pp":Sigma_pp})

    mus = [1/10, 1/3, 1.0, 3.0, 10.0]
    for mu in mus:
        I = I_dimreg_finite(mu, m=m)
        Sigma_pp = g**2 * I
        rows.append({"scheme":"DimReg_finite", "scale":mu, "I":I, "I_err":0.0, "Sigma_pp":Sigma_pp})

    df = pd.DataFrame(rows)
    df.to_csv(outdir/"sigma_pp_scan.csv", index=False)

    # simple plot
    plt.figure()
    for scheme in df.scheme.unique():
        sub=df[df.scheme==scheme]
        plt.plot(sub.scale, sub.Sigma_pp, marker="o", label=scheme)
    plt.xscale("log")
    plt.xlabel("regulator scale (M or μ)")
    plt.ylabel("Σ_R''(0) (example units)")
    plt.title("Regulator scan (example) for Σ_R''(0)")
    plt.grid(True, ls=":")
    plt.legend()
    plt.tight_layout()
    plt.savefig(outdir/"sigma_pp_scan.png", dpi=150)
    plt.close()

    print("Wrote", outdir/"sigma_pp_scan.csv")
