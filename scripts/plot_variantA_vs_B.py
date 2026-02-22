#!/usr/bin/env python3
"""plot_variantA_vs_B.py

Generates a paired ΔΛ1.4(σ) figure comparing Variant A vs Variant B_exploratory.

Inputs
------
- outputs/deltaLambda_sigma_panel.csv (produced by scripts/build_deltaLambda_sigma_panel.py)

Outputs
-------
- figures/variantA_vs_B_exploratory_deltaLambda_sigma_panel.png
- figures/variantA_vs_B_exploratory_deltaLambda_sigma_panel.pdf
- outputs/paired_residuals.csv
- figures/variantA_vs_B_caption.txt
"""
from __future__ import annotations
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

def main() -> None:
    src = Path("outputs/deltaLambda_sigma_panel.csv")
    if not src.exists():
        raise SystemExit("Missing outputs/deltaLambda_sigma_panel.csv; run scripts/build_deltaLambda_sigma_panel.py")

    df = pd.read_csv(src)
    eos_order = list(dict.fromkeys(df["EOS"].tolist()))
    sigmas = sorted(df["sigma"].unique())

    fig, axes = plt.subplots(3, 1, figsize=(8, 11), sharex=True, gridspec_kw={"height_ratios": [3, 1.3, 1.3]})
    ax1, ax2, ax3 = axes

    # Top panel: ΔΛ vs σ
    for eos in eos_order:
        for variant, ls, marker in [("A", "-", "o"), ("B_exploratory", "--", "s")]:
            sel = df[(df.EOS == eos) & (df.variant == variant)].sort_values("sigma")
            if sel.empty:
                continue
            ax1.plot(sel["sigma"], sel["deltaLambda"], linestyle=ls, marker=marker,
                     label=f"{eos}" if variant == "A" else f"{eos} (B_expl)")
    ax1.set_ylabel("ΔΛ1.4 (absolute)")
    ax1.set_title("ΔΛ1.4 vs σ — Variant A vs Variant B_exploratory")
    ax1.grid(True, linestyle=":")
    ax1.legend(fontsize=8)

    # Middle panel: epsratio bands
    ax2.axhspan(0.0, 0.10, alpha=0.15)
    ax2.axhspan(0.10, 0.30, alpha=0.15)
    ax2.axhspan(0.30, max(0.35, float(df["max_epsratio"].max()) + 0.05), alpha=0.15)
    for eos in eos_order:
        sel = df[(df.EOS == eos) & (df.variant == "A")].sort_values("sigma")
        ax2.plot(sel["sigma"], sel["max_epsratio"], marker="o", linestyle="-")
    ax2.set_ylabel("max_r|epsratio|")
    ax2.grid(True, linestyle=":")
    ax2.set_ylim(bottom=0)

    # Bottom panel: residuals
    rows = []
    for eos in eos_order:
        for s in sigmas:
            a = df[(df.EOS == eos) & (df.variant == "A") & (df.sigma == s)]
            b = df[(df.EOS == eos) & (df.variant == "B_exploratory") & (df.sigma == s)]
            if len(a) != 1 or len(b) != 1:
                continue
            rows.append({
                "EOS": eos,
                "sigma": s,
                "residual": float(b.iloc[0]["deltaLambda"]) - float(a.iloc[0]["deltaLambda"]),
                "derived": bool(b.iloc[0].get("derived", False)),
            })
    res = pd.DataFrame(rows)
    if not res.empty:
        for eos in eos_order:
            sel = res[res.EOS == eos].sort_values("sigma")
            ax3.plot(sel["sigma"], sel["residual"], marker="o", linestyle="-")
            # mark derived points as open markers
            for _, r in sel[sel["derived"]].iterrows():
                ax3.plot(r["sigma"], r["residual"], marker="o", markerfacecolor="none",
                         markeredgecolor="k", markersize=8)
        ax3.axhline(0, color="k", linestyle=":")
    ax3.set_ylabel("ΔΛ_B − ΔΛ_A")
    ax3.set_xlabel("σ")
    ax3.grid(True, linestyle=":")

    Path("figures").mkdir(exist_ok=True)
    Path("outputs").mkdir(exist_ok=True)
    png = Path("figures/variantA_vs_B_exploratory_deltaLambda_sigma_panel.png")
    pdf = Path("figures/variantA_vs_B_exploratory_deltaLambda_sigma_panel.pdf")
    fig.tight_layout()
    fig.savefig(png, dpi=300)
    fig.savefig(pdf)
    plt.close(fig)

    res.to_csv(Path("outputs/paired_residuals.csv"), index=False)

    caption = (
        "Figure Y — Paired ΔΛ1.4(σ) comparison for Variant A (inertial only; solid) and "
        "Variant B_exploratory (inertial + source; dashed). Top: absolute ΔΛ1.4 relative to σ=0. "
        "Middle: max_r|epsratio| with interpretability bands. Bottom: residual ΔΛ_B − ΔΛ_A. "
        "Open markers indicate σ=0.04 values for Variant B that are linearly scaled from the σ=0.06 gravity-insertion run "
        "(flagged derived=true in outputs/deltaLambda_sigma_panel.csv). Data: outputs/deltaLambda_sigma_panel.csv and outputs/paired_residuals.csv."
    )
    Path("figures/variantA_vs_B_caption.txt").write_text(caption, encoding="utf-8")

    print("Wrote figure and residuals:")
    print(" -", png)
    print(" -", pdf)
    print(" - outputs/paired_residuals.csv")

if __name__ == "__main__":
    main()
