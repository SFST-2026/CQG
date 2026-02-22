#!/usr/bin/env python3
"""scan_gGamma_small.py

Tiny end-to-end smoke test for the (g, Gamma) mapping workflow.
Intended to be run with SFST_DRYRUN=1 unless you've wired a real solver.

Outputs:
- outputs/scan_mapping_small/scan_grid.csv
- outputs/scan_mapping_small/audit_index.csv
"""
from __future__ import annotations

from pathlib import Path
import pandas as pd

from scan_wrappers import compute_tov_case

OUTDIR = Path("outputs/scan_mapping_small")
OUTDIR.mkdir(parents=True, exist_ok=True)

def main():
    chi_ref = 1.0
    eos_list = ["SLy", "AP4"]

    points = [
        # Null tests
        {"g": 0.0,   "Gamma": 1e2,  "seed": 111111},
        {"g": 1e-4,  "Gamma": 1e12, "seed": 222222},
        # Small perturbative points
        {"g": 1e-5,  "Gamma": 1e2,  "seed": 333333},
        {"g": 3e-5,  "Gamma": 1e2,  "seed": 444444},
    ]

    rows, audit = [], []
    for eos in eos_list:
        for p in points:
            g = float(p["g"]); Gamma=float(p["Gamma"]); seed=int(p["seed"])
            sigma = (g*g)/Gamma * chi_ref
            run_tag = f"{eos}_SMOKE_g{g:.1e}_G{Gamma:.1e}_s{seed}"
            res = compute_tov_case(eos=eos, sigma=sigma, run_tag=run_tag, extra={"g": g, "Gamma": Gamma, "seed": seed})
            rows.append({**res, "g": g, "Gamma": Gamma})
            audit.append({
                "run_id": res.get("run_id"),
                "eos": eos,
                "g": g,
                "Gamma": Gamma,
                "sigma": sigma,
                "status": "DONE" if res.get("converged") else "FAILED",
                "path": f"outputs/diagnostics/{res.get('run_id')}",
                "reason": res.get("error",""),
            })

    pd.DataFrame(rows).to_csv(OUTDIR / "scan_grid.csv", index=False)
    pd.DataFrame(audit).to_csv(OUTDIR / "audit_index.csv", index=False)
    print(f"Wrote {OUTDIR/'scan_grid.csv'}")
    print(f"Wrote {OUTDIR/'audit_index.csv'}")

if __name__ == "__main__":
    main()
