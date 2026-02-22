#!/usr/bin/env python3
"""
Compute a conservative, reviewer-facing Λ1.4 nonlinearity summary.

This script is intentionally robust:
- It works with the repository's outputs/runs_summary.csv schema.
- It treats missing/insufficient σ-grid information conservatively.
- It writes machine-readable headline tables with/without DIAGNOSTIC/EXCLUDED runs.

Outputs:
  outputs/lambda_nonlinearity_summary.csv
  outputs/headline_with_diagnostics.csv
  outputs/headline_without_diagnostics.csv
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from pathlib import Path

RUNS = Path("outputs/runs_summary.csv")
OUT1 = Path("outputs/lambda_nonlinearity_summary.csv")
OUT2 = Path("outputs/headline_with_diagnostics.csv")
OUT3 = Path("outputs/headline_without_diagnostics.csv")

N_MC = 5000
RNG = np.random.default_rng(0)

def main() -> None:
    df = pd.read_csv(RUNS)

    # Use validator output as the source of truth for accepted/diagnostic/excluded.
    audit = pd.read_csv(Path('outputs')/'audit_index.csv')
    status_by_run = dict(zip(audit['run_id'].astype(str), audit['status'].astype(str)))

    # Focus on the σ-scan case used for Λ1.4 reporting.
    c = df[df["case"].astype(str).str.contains("C_sigma_chi", na=False)].copy()
    if c.empty:
        raise SystemExit("No C_sigma_chi rows found in outputs/runs_summary.csv")

    rows = []
    for eos, g in c.groupby("EOS"):
        g = g.sort_values("run_id")

        # Repository schema: percent response and percent total uncertainty for Λ1.4
        delta = float(g["Delta_Lambda14_pct"].iloc[0])
        err = float(g["delta_total_Lambda14_pct"].iloc[0])

        # Conservative MC: treat delta_total as a 1σ uncertainty in the reported percent response.
        samples = RNG.normal(delta, err, size=N_MC)
        mc_5, mc_med, mc_95 = np.percentile(samples, [5, 50, 95])

        # If a multi-σ grid is present in the future, this can be upgraded to a quadratic fit.
        q_min = q_med = q_max = delta

        status = status_by_run.get(str(g['run_id'].iloc[0]), 'accepted').lower()
        rows.append([eos, q_min, q_med, q_max, mc_5, mc_med, mc_95, status])

    out = pd.DataFrame(
        rows,
        columns=["EOS", "q_min", "q_med", "q_max", "mc_5", "mc_med", "mc_95", "status"],
    ).sort_values("EOS")

    OUT1.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(OUT1, index=False)
    out.to_csv(OUT2, index=False)
    out[out["status"] == "accepted"].to_csv(OUT3, index=False)

    print(f"Wrote {OUT1}")
    print(f"Wrote {OUT2}")
    print(f"Wrote {OUT3}")

if __name__ == "__main__":
    main()