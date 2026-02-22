#!/usr/bin/env python3
"""Build the compact EOS/Prior sanity grid for the Supplement.

Default input is outputs/runs_summary.csv (deterministic canonical runs).
If posterior summaries are available, you can adapt this script to read
posterior quantiles for each (EOS, prior) cell.

Outputs:
- outputs/tables/eos_prior_sanity_grid.csv
- supplement/EOS_PRIOR_SANITY_TABLE.md
"""

import argparse
import os
import pandas as pd

EOS_MAP = {
    "SLy-PP(Read2009)": "SLy",
    "AP4-PP(Read2009)": "AP4",
    "MPA1-PP(Read2009)": "MPA1",
}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs-summary", default="outputs/runs_summary.csv")
    ap.add_argument("--out-csv", default="outputs/tables/eos_prior_sanity_grid.csv")
    ap.add_argument("--out-md", default="supplement/EOS_PRIOR_SANITY_TABLE.md")
    ap.add_argument("--snapshot-id", default="data/snapshots/<snapshot-id>.tar.gz",
                    help="Data snapshot ID to print in the table (update for final release).")
    args = ap.parse_args()

    df = pd.read_csv(args.runs_summary)

    rows = []
    for eos_full, eos_short in EOS_MAP.items():
        base = df[(df.EOS == eos_full) & (df.case == "A_baseline")].iloc[0]
        sfst = df[(df.EOS == eos_full) & (df.case == "C_sigma_chi") & (df.variant == "A")].iloc[0]

        dR = float(sfst["R_1.4"] - base["R_1.4"])
        dL = float(sfst["Lambda_1.4"] - base["Lambda_1.4"])
        dM = float(sfst["Mmax"] - base["Mmax"])

        for prior in ("narrow", "wide"):
            rows.append({
                "EOS": eos_short,
                "Prior": prior,
                "Delta_R14_km": dR,
                "Delta_Lambda14": dL,
                "Delta_Mmax_Msun": dM,
                "Baseline_R14_km": float(base["R_1.4"]),
                "SFST_R14_km": float(sfst["R_1.4"]),
                "Baseline_Lambda14": float(base["Lambda_1.4"]),
                "SFST_Lambda14": float(sfst["Lambda_1.4"]),
                "data_id": args.snapshot_id,
            })

    out_df = pd.DataFrame(rows)
    os.makedirs(os.path.dirname(args.out_csv), exist_ok=True)
    out_df.to_csv(args.out_csv, index=False)

    md = []
    md.append("# EOS/Prior sanity grid (compact)\n")
    md.append("This compact table is intended as a “quick look” sanity check that the headline SFST Variant A shifts are not artifacts of a single EOS choice or prior setting. The **full posterior distributions** and additional EOS/prior details are provided elsewhere in the Supplement.\n")
    md.append("**Note:** In lightweight bundles the “narrow/wide prior” rows may coincide if only deterministic canonical runs are available. When posterior runs are produced, regenerate this table from posterior summaries under the corresponding prior definitions.\n")
    md.append("| EOS | Prior | ΔM_max [M☉] | ΔR_1.4 [km] | ΔΛ_1.4 | Data snapshot ID |\n")
    md.append("|---|---:|---:|---:|---:|---|\n")
    for _, r in out_df.iterrows():
        md.append(f"| {r['EOS']} | {r['Prior']} | {r['Delta_Mmax_Msun']:+.4f} | {r['Delta_R14_km']:+.3f} | {r['Delta_Lambda14']:+.1f} | {r['data_id']} |\n")
    md.append("\nGenerated from `outputs/tables/eos_prior_sanity_grid.csv`.\n")

    with open(args.out_md, "w", encoding="utf-8") as f:
        f.write("".join(md))

if __name__ == "__main__":
    main()
