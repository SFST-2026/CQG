#!/usr/bin/env python3
"""fit_sensitivities.py

Produces compact, Word-ready sensitivity tables for representative EOS.

Inputs
------
- outputs/summary_canonical_runs.csv  (produced by scripts/run_canonical_runs.py)

Outputs
-------
- outputs/sensitivities_table.csv         (min/med/max strings; Word/CSV friendly)
- outputs/sensitivities_with_errors.csv   (wide numeric table incl. half-range)

Notes
-----
The table reports finite-difference slopes (Δobservable/Δσ) relative to the EOS baseline (σ=0),
computed for the two canonical σ points σ=0.04 (legacy) and σ=0.06 (sigma*chi).
"""
from __future__ import annotations
from pathlib import Path
import pandas as pd
import numpy as np

EOS_REPRESENTATIVE = ["Poly2(toy)", "SLy-PP(Read2009)", "AP4-PP(Read2009)"]

def _slopes_from_canonical(df: pd.DataFrame, eos: str) -> dict:
    g = df[df["EOS"] == eos].copy()
    base = g[g["case"] == "A_baseline"].iloc[0]
    baseL = float(base["Lambda_1.4"])
    baseM = float(base["Mmax"])
    baseR = float(base["R_1.4"])
    out = {}
    for case in ["B_legacy", "C_sigma_chi"]:
        r = g[g["case"] == case].iloc[0]
        sigma = float(r["sigma_vac"])
        out[case] = {
            "sigma": sigma,
            "S_M": (float(r["Mmax"]) - baseM) / sigma,
            "S_R": (float(r["R_1.4"]) - baseR) / sigma,
            "S_L": (float(r["Lambda_1.4"]) - baseL) / sigma,
        }
    return out

def main() -> None:
    outdir = Path("outputs")
    src = outdir / "summary_canonical_runs.csv"
    if not src.exists():
        raise SystemExit("Missing outputs/summary_canonical_runs.csv; run: python scripts/run_canonical_runs.py")

    df = pd.read_csv(src)
    rows = []
    wide = []

    # status from validator outputs (if present)
    status_map = {}
    diag_path = outdir / "diagnostic.csv"
    if diag_path.exists():
        diag = pd.read_csv(diag_path)
        for eos in EOS_REPRESENTATIVE:
            status_map[eos] = "diagnostic" if (diag.get("EOS", pd.Series([], dtype=str)) == eos).any() else "accepted"
    else:
        status_map = {e: "unknown" for e in EOS_REPRESENTATIVE}

    for eos in EOS_REPRESENTATIVE:
        s = _slopes_from_canonical(df, eos)

        def minmedmax(key: str):
            vals = [s["B_legacy"][key], s["C_sigma_chi"][key]]
            return float(np.min(vals)), float(np.median(vals)), float(np.max(vals))

        smn, smd, smx = minmedmax("S_M")
        rmn, rmd, rmx = minmedmax("S_R")
        lmn, lmd, lmx = minmedmax("S_L")

        wide.append({
            "EOS": eos,
            "S_M_min": smn, "S_M_med": smd, "S_M_max": smx,
            "S_R_min": rmn, "S_R_med": rmd, "S_R_max": rmx,
            "S_L_min": lmn, "S_L_med": lmd, "S_L_max": lmx,
            "status": status_map.get(eos, "unknown"),
            "sigma_spans": "0.04,0.06",
        })

        rows.append({
            "EOS": eos,
            "S_M (ΔM_max/Δσ) min;med;max": f"{smn:.3f};{smd:.3f};{smx:.3f}",
            "S_R (ΔR_1.4/Δσ) min;med;max": f"{rmn:.2f};{rmd:.2f};{rmx:.2f}",
            "S_Λ (ΔΛ_1.4/Δσ) min;med;max": f"{lmn:.2e};{lmd:.2e};{lmx:.2e}",
            "status": status_map.get(eos, "unknown"),
            "sigma_spans": "0.04,0.06",
        })

    wide_df = pd.DataFrame(wide)
    wide_df["S_M_half_range"] = 0.5 * (wide_df["S_M_max"] - wide_df["S_M_min"])
    wide_df["S_R_half_range"] = 0.5 * (wide_df["S_R_max"] - wide_df["S_R_min"])
    wide_df["S_L_half_range"] = 0.5 * (wide_df["S_L_max"] - wide_df["S_L_min"])

    (outdir / "sensitivities_table.csv").write_text(pd.DataFrame(rows).to_csv(index=False), encoding="utf-8")
    wide_df.to_csv(outdir / "sensitivities_with_errors.csv", index=False)

    print("Wrote:")
    print(" - outputs/sensitivities_table.csv")
    print(" - outputs/sensitivities_with_errors.csv")

if __name__ == "__main__":
    main()
