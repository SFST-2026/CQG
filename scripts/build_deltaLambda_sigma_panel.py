#!/usr/bin/env python3
"""build_deltaLambda_sigma_panel.py

Builds the per-σ panel CSV used by the Variant A vs Variant B_exploratory paired figure.

Inputs
------
- outputs/summary_canonical_runs.csv

Outputs
-------
- outputs/deltaLambda_sigma_panel.csv
"""
from __future__ import annotations
from pathlib import Path
import pandas as pd

EOS_REPRESENTATIVE = ["Poly2(toy)", "SLy-PP(Read2009)", "AP4-PP(Read2009)"]

def main() -> None:
    src = Path("outputs/summary_canonical_runs.csv")
    if not src.exists():
        raise SystemExit("Missing outputs/summary_canonical_runs.csv; run scripts/run_canonical_runs.py")

    df = pd.read_csv(src)
    df = df[df["EOS"].isin(EOS_REPRESENTATIVE)].copy()

    rows = []
    for eos in EOS_REPRESENTATIVE:
        g = df[df["EOS"] == eos]
        base = g[g["case"] == "A_baseline"].iloc[0]
        baseL = float(base["Lambda_1.4"])

        # Variant A points on σ grid
        for case in ["B_legacy", "C_sigma_chi"]:
            r = g[g["case"] == case].iloc[0]
            sigma = float(r["sigma_vac"])
            L = float(r["Lambda_1.4"])
            dL = L - baseL
            rows.append({
                "EOS": eos, "variant": "A", "sigma": sigma,
                "Lambda_1.4": L, "deltaLambda": dL, "deltaLambda_frac": dL / baseL,
                "max_epsratio": abs(sigma * float(r["chi_vac"]) * float(r["screening_factor"])),
                "inc_g": bool(r["inc_g"]), "source_case": case, "derived": False,
            })

        # Variant B_exploratory: σ=0.06 is directly available as D_sigma_chi_gravity; σ=0.04 is linearly scaled
        rD = g[g["case"] == "D_sigma_chi_gravity"].iloc[0]
        Ld = float(rD["Lambda_1.4"])
        dL = Ld - baseL
        rows.append({
            "EOS": eos, "variant": "B_exploratory", "sigma": 0.06,
            "Lambda_1.4": Ld, "deltaLambda": dL, "deltaLambda_frac": dL / baseL,
            "max_epsratio": 0.06, "inc_g": True, "source_case": "D_sigma_chi_gravity", "derived": False,
        })
        dL04 = dL * (0.04 / 0.06)
        rows.append({
            "EOS": eos, "variant": "B_exploratory", "sigma": 0.04,
            "Lambda_1.4": baseL + dL04, "deltaLambda": dL04, "deltaLambda_frac": dL04 / baseL,
            "max_epsratio": 0.04, "inc_g": True, "source_case": "D_sigma_chi_gravity_scaled", "derived": True,
        })

        # Baselines
        for variant in ["A", "B_exploratory"]:
            rows.append({
                "EOS": eos, "variant": variant, "sigma": 0.0,
                "Lambda_1.4": baseL, "deltaLambda": 0.0, "deltaLambda_frac": 0.0,
                "max_epsratio": 0.0, "inc_g": False, "source_case": "A_baseline", "derived": False,
            })

    out = pd.DataFrame(rows).sort_values(["EOS", "variant", "sigma"])
    out_path = Path("outputs/deltaLambda_sigma_panel.csv")
    out.to_csv(out_path, index=False)
    print("Wrote", out_path)

if __name__ == "__main__":
    main()
