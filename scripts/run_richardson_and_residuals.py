import os
import sys

# Ensure repo root is importable when this script is executed as a file.
_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sfst_qfis_repro import make_piecewise_eos, solve_star, pick_star_by_mass

def residual_profile(profile):
    r = np.asarray(profile["r"])
    m = np.asarray(profile["m"])
    eps = np.asarray(profile["eps_grav"])
    dm_dr_num = np.gradient(m, r, edge_order=2)
    dm_dr_rhs = 4*np.pi*r**2*eps
    res = dm_dr_num - dm_dr_rhs
    return r, res

def main():
    outdir = Path("outputs/diagnostics")
    outdir.mkdir(parents=True, exist_ok=True)

    eos = make_piecewise_eos(34.384, 3.005, 2.988, 2.851, "SLy-PP(Read2009)")
    levels = [
        ("T1", 3e-6, 1e-9, 8e4),
        ("T2", 1e-6, 3e-10, 4e4),
        ("T3", 3e-7, 1e-10, 2e4),
    ]
    rows=[]
    for label, rtol, atol, max_step in levels:
        df0 = solve_star.scan_family(eos, sigma_vac=0.0, chi_vac=1.0, screening_factor=1.0, include_in_gravity=False,
                                     rtol=rtol, atol=atol, store_profiles=False)
        df1 = solve_star.scan_family(eos, sigma_vac=0.06, chi_vac=1.0, screening_factor=1.0, include_in_gravity=False,
                                     rtol=rtol, atol=atol, store_profiles=False)
        M0 = float(df0["M_msun"].max()); M1 = float(df1["M_msun"].max())
        rows.append({"level":label,"rtol":rtol,"atol":atol,"max_step":max_step,"Mmax_baseline":M0,"Mmax_sigma":M1,"DeltaMmax":M1-M0})
    rich = pd.DataFrame(rows)
    rich.to_csv(outdir/"richardson_levels.csv", index=False)

    plt.figure(figsize=(6,4))
    plt.plot(rich["level"], rich["DeltaMmax"], marker="o")
    plt.xlabel("Tolerance level (coarser→finer)")
    plt.ylabel("ΔM_max [M_sun]")
    plt.title("Convergence ladder for ΔM_max (SLy, Variant A)")
    plt.grid(True, which="both", ls=":")
    plt.tight_layout()
    plt.savefig(outdir/"richardson_DeltaMmax.png", dpi=200)

    fam = solve_star.scan_family(eos, sigma_vac=0.0, chi_vac=1.0, screening_factor=1.0, include_in_gravity=False,
                                 rtol=3e-7, atol=1e-10, store_profiles=True)
    prof = pick_star_by_mass(fam, 1.4)
    r, res = residual_profile(prof)
    plt.figure(figsize=(6,4))
    plt.plot(r, np.abs(res))
    plt.yscale("log")
    plt.xlabel("r [geom]")
    plt.ylabel("|dm/dr - 4πr²ε|")
    plt.title("Constraint residual along radius (SLy, ~1.4 M⊙)")
    plt.grid(True, which="both", ls=":")
    plt.tight_layout()
    plt.savefig(outdir/"residual_trace.png", dpi=200)

    print("Wrote diagnostics to outputs/diagnostics/")

if __name__ == "__main__":
    main()
