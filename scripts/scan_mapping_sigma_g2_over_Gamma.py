#!/usr/bin/env python3
"""scan_mapping_sigma_g2_over_Gamma.py

Repo-integrated helper script: build a (g, Gamma) grid, map to sigma = g^2/Gamma * chi_ref,
and run the existing TOV pipeline for each parameter set.

IMPORTANT:
- This script is a *driver*: you must connect `compute_tov_case(...)` to your project’s
  existing run function(s). The hook is intentionally small and local.
- Outputs are written under outputs/scan_mapping/ and figures/scan_mapping/.
"""

import os
import math
import json
import numpy as np
import pandas as pd

# ---- user config ----
CHI_REF = 1.0
LOG10_G_MIN, LOG10_G_MAX = -6.0, -1.0
LOG10_GAMMA_MIN, LOG10_GAMMA_MAX = -3.0, 3.0
N_G, N_GAMMA = 12, 12
EOS_LIST = ["SLy-PP(Read2009)", "AP4-PP(Read2009)", "Poly2(toy)"]

OUT_DIR = "outputs/scan_mapping"
FIG_DIR = "figures/scan_mapping"
os.makedirs(OUT_DIR, exist_ok=True)
os.makedirs(FIG_DIR, exist_ok=True)

from scan_wrappers import compute_tov_case  # template wrapper (wire _call_tov_entrypoint)

def classify_run(max_epsratio: float, wfaktor_max: float, newton_residual: float) -> str:
    # Mirror thresholds used in config/validate_config.yaml (adjust if needed)
    if max_epsratio <= 0.10 and wfaktor_max < 1e4 and newton_residual < 1e-6:
        return "ACCEPTED"
    if max_epsratio <= 0.30:
        return "STRESS"
    return "DIAGNOSTIC"

def main():
    g_vals = np.logspace(LOG10_G_MIN, LOG10_G_MAX, N_G)
    gamma_vals = np.logspace(LOG10_GAMMA_MIN, LOG10_GAMMA_MAX, N_GAMMA)

    rows = []
    for eos in EOS_LIST:
        for g in g_vals:
            for Gamma in gamma_vals:
                sigma = (g**2) / Gamma * CHI_REF
                run_tag = f"{eos}_g{g:.2e}_G{Gamma:.2e}"
                try:
                    res = compute_tov_case(eos=eos, sigma=float(sigma), run_tag=run_tag, extra={"g":float(g), "Gamma":float(Gamma)})
                    status = classify_run(float(res.get("max_epsratio", 999.0)),
                                          float(res.get("wfaktor_max", 1e99)),
                                          float(res.get("newton_final_residual", 1.0)))
                    rows.append({
                        "run_id": res.get("run_id"),
                        "eos": eos,
                        "g": float(g),
                        "Gamma": float(Gamma),
                        "sigma": float(sigma),
                        "M_max": res.get("M_max"),
                        "R_1p4": res.get("R_1p4"),
                        "Lambda_1p4": res.get("Lambda_1p4"),
                        "max_epsratio": res.get("max_epsratio"),
                        "wfaktor_max": res.get("wfaktor_max"),
                        "newton_final_residual": res.get("newton_final_residual"),
                        "converged": res.get("converged"),
                        "status": status
                    })
                except Exception as e:
                    rows.append({
                        "run_id": None, "eos": eos, "g": float(g), "Gamma": float(Gamma), "sigma": float(sigma),
                        "status": "FAILED", "error": str(e)
                    })

    df = pd.DataFrame(rows)
    out_csv = os.path.join(OUT_DIR, "scan_grid.csv")
    df.to_csv(out_csv, index=False)
    print(f"Wrote {out_csv} with {len(df)} rows.")

if __name__ == "__main__":
    main()
