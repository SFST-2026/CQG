#!/usr/bin/env python3
"""
Figure X — Compact numerical stability overview (Panels A–C)

Inputs (CSV):
  - outputs/diagnostics/*/richardson.csv
  - outputs/diagnostics/*/epsratio_profile.csv
  - outputs/scan_summary.csv

Outputs:
  - figures/figX_stability_convergence.png
  - figures/figX_stability_epsratio.png
  - figures/figX_stability_errordist.png
  - figures/figX_numerical_stability_overview.png
"""
import os
import glob
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OUT_FIG = os.path.join(REPO_ROOT, "figures")
os.makedirs(OUT_FIG, exist_ok=True)

# --- Load scan summary (classification + delta_total) ---
scan = pd.read_csv(os.path.join(REPO_ROOT, "outputs", "scan_summary.csv"))

# Total discretization error proxy (max across reported observables)
scan["delta_total_pct"] = scan[["delta_total_Mmax_pct","delta_total_R14_pct","delta_total_Lambda14_pct"]].max(axis=1)

# Cap extreme sentinel values for plotting (kept in data; capped in axis)
CAP = 200.0
scan["delta_total_pct_plot"] = scan["delta_total_pct"].clip(upper=CAP)

# --- Collect diagnostic ladders and epsratio profiles ---
diag_root = os.path.join(REPO_ROOT, "outputs", "diagnostics")
rich_files = sorted(glob.glob(os.path.join(diag_root, "*", "richardson.csv")))
eps_files  = sorted(glob.glob(os.path.join(diag_root, "*", "epsratio_profile.csv")))

# Choose three representative cases by run_id (must exist under outputs/diagnostics/<run_id>/)
REP_RUN_IDS = [
    "SLyPPRead2009_C_sigma_chi",
    "AP4PPRead2009_C_sigma_chi",
    "Poly2toy_C_sigma_chi",
]

# Convenience: map run_id -> EOS label (from scan_summary)
runid_to_eos = {r["run_id"]: r["EOS"] for _, r in scan.drop_duplicates("run_id")[["run_id","EOS"]].iterrows()}

# --- Panel A data: ladder (max_step vs Mmax, R_1.4, Lambda_1.4) ---
ladder_rows = []
for rid in REP_RUN_IDS:
    f = os.path.join(diag_root, rid, "richardson.csv")
    if not os.path.exists(f):
        raise FileNotFoundError(f"Missing ladder CSV: {f}")
    df = pd.read_csv(f)
    df["run_id"] = rid
    df["EOS"] = runid_to_eos.get(rid, rid)
    ladder_rows.append(df)
ladder = pd.concat(ladder_rows, ignore_index=True)

# --- Panel B data: epsratio(r) ---
eps_rows = []
for rid in REP_RUN_IDS:
    f = os.path.join(diag_root, rid, "epsratio_profile.csv")
    if not os.path.exists(f):
        raise FileNotFoundError(f"Missing epsratio profile CSV: {f}")
    df = pd.read_csv(f)
    df["run_id"] = rid
    df["EOS"] = runid_to_eos.get(rid, rid)
    eps_rows.append(df)
epsprof = pd.concat(eps_rows, ignore_index=True)

# --- Styling ---
# Colors: one per EOS (use matplotlib default cycle deterministically)
eos_list = [runid_to_eos.get(rid, rid) for rid in REP_RUN_IDS]
cycle = plt.rcParams["axes.prop_cycle"].by_key()["color"]
eos_to_color = {eos: cycle[i % len(cycle)] for i, eos in enumerate(eos_list)}

obs_styles = {
    "Mmax":      dict(ls="-",  marker="o", label=r"$M_{\max}$"),
    "R_1.4":     dict(ls="--", marker="s", label=r"$R_{1.4}$"),
    "Lambda_1.4":dict(ls=":",  marker="^", label=r"$\Lambda_{1.4}$"),
}

# -------------------------
# Panel A — Convergence ladder
# -------------------------
figA, axA = plt.subplots(figsize=(6.6, 4.8))
for eos in eos_list:
    df_e = ladder[ladder["EOS"]==eos].sort_values("max_step", ascending=False)  # larger step = coarser
    for obs, sty in obs_styles.items():
        axA.plot(
            df_e["max_step"], df_e[obs],
            color=eos_to_color[eos],
            ls=sty["ls"], marker=sty["marker"], ms=5
        )

axA.set_xscale("log")
axA.invert_xaxis()
axA.set_xlabel("Grid resolution proxy: max_step (smaller = finer)")
axA.set_ylabel("Observable value (units as in Table)")
axA.set_title("Panel A — Convergence ladder (representative observables)")

eos_handles = [Line2D([0],[0], color=eos_to_color[e], lw=2, label=e) for e in eos_list]
obs_handles = [Line2D([0],[0], color="black", lw=2, ls=sty["ls"], marker=sty["marker"], label=sty["label"])
               for sty in obs_styles.values()]
leg1 = axA.legend(handles=eos_handles, title="EOS", loc="upper left", frameon=True)
axA.add_artist(leg1)
axA.legend(handles=obs_handles, title="Observable", loc="lower left", frameon=True)

# Inset: estimated convergence order p (from outputs/convergence_summary.csv)
conv = pd.read_csv(os.path.join(REPO_ROOT, "outputs", "convergence_summary.csv"))
inset = axA.inset_axes([0.62,0.58,0.35,0.35])
inset.axis("off")
lines=[]
for rid in ["SLyPPRead2009_C_sigma_chi","AP4PPRead2009_C_sigma_chi"]:
    p = conv.loc[conv["run_id"]==rid, "p_est"]
    if len(p):
        eos = runid_to_eos.get(rid, rid)
        lines.append(f"{eos.split('-')[0]}: p ≈ {float(p.iloc[0]):.2g}")
inset.text(0,1,"\n".join(lines), va="top")
inset.set_title("Estimated p", fontsize=9)

figA.tight_layout()
figA_path = os.path.join(OUT_FIG, "figX_stability_convergence.png")
figA.savefig(figA_path, dpi=450, bbox_inches="tight")

# -------------------------
# Panel B — epsratio profiles with interpretability bands
# -------------------------
figB, axB = plt.subplots(figsize=(6.6, 4.8))

# Interpretability bands
axB.axhspan(-0.10, 0.10, alpha=0.18)  # green zone implied
axB.axhspan( 0.10, 0.30, alpha=0.14)  # amber
axB.axhspan(-0.30,-0.10, alpha=0.14)  # amber
axB.axhspan( 0.30, 1.00, alpha=0.10)  # red
axB.axhspan(-1.00,-0.30, alpha=0.10)  # red

for eos in eos_list:
    df = epsprof[epsprof["EOS"]==eos]
    axB.plot(df["r_km"], df["epsratio"], lw=1.2, color=eos_to_color[eos], label=eos)
    m = float(np.max(np.abs(df["epsratio"].values)))
    # annotate near 65% radius
    r_anno = float(df["r_km"].max())*0.65
    eps_anno = float(df.loc[(df["r_km"]-r_anno).abs().idxmin(), "epsratio"])
    axB.annotate(f"max|ε|={m:.2f}", xy=(r_anno, eps_anno), fontsize=8, color=eos_to_color[eos])

axB.axhline(0, lw=0.8)
axB.set_xlabel("Radius r (km)")
axB.set_ylabel("epsratio(r)")
axB.set_title("Panel B — Radial epsratio profiles with interpretability bands")
ylim = max(0.35, float(np.max(np.abs(epsprof["epsratio"].values)))*1.25)
axB.set_ylim(-ylim, ylim)
axB.legend(loc="upper right", frameon=True, fontsize=8)

figB.tight_layout()
figB_path = os.path.join(OUT_FIG, "figX_stability_epsratio.png")
figB.savefig(figB_path, dpi=450, bbox_inches="tight")

# -------------------------
# Panel C — Error distribution and classification
# -------------------------
figC, axC = plt.subplots(figsize=(12.0, 4.8))

status_order = ["accepted","stress","diagnostic","excluded"]
status_colors = {
    "accepted": (0.0,0.6,0.0,0.55),
    "stress": (0.85,0.55,0.0,0.55),
    "diagnostic": (0.75,0.0,0.0,0.55),
    "excluded": (0.4,0.0,0.0,0.55),
}

bins = np.linspace(0, CAP, 35)
for status in status_order:
    df = scan[scan["obs_status"]==status]
    if len(df)==0:
        continue
    axC.hist(df["delta_total_pct_plot"], bins=bins, alpha=0.6,
             label=status, color=status_colors.get(status,(0.2,0.2,0.2,0.55)))

axC.set_xlabel(r"Total discretization error proxy $\delta_{\mathrm{total}}$ (%)")
axC.set_ylabel("Frequency")
axC.set_title("Panel C — Error distribution and automated classification")

# CDF on right axis
axC2 = axC.twinx()
vals = np.sort(scan["delta_total_pct_plot"].values)
cum = np.arange(1, len(vals)+1)/len(vals)
axC2.plot(vals, cum, lw=1.5, color="black")
axC2.set_ylabel("Cumulative fraction")
axC2.set_ylim(0, 1.0)

for thr in [20, 50]:
    axC.axvline(thr, lw=1.0, ls="--", color="black")
    axC.text(thr+1, axC.get_ylim()[1]*0.9, f"{thr}%", fontsize=9)

axC.legend(loc="upper right", frameon=True)

figC.tight_layout()
figC_path = os.path.join(OUT_FIG, "figX_stability_errordist.png")
figC.savefig(figC_path, dpi=450, bbox_inches="tight")

# -------------------------
# Combined multi-panel figure (A–C)
# -------------------------
fig = plt.figure(figsize=(12, 10))
gs = fig.add_gridspec(2, 2, height_ratios=[1,1], width_ratios=[1,1], hspace=0.28, wspace=0.25)

ax1 = fig.add_subplot(gs[0,0])
ax2 = fig.add_subplot(gs[0,1])
ax3 = fig.add_subplot(gs[1,:])

# Re-draw Panel A on ax1
for eos in eos_list:
    df_e = ladder[ladder["EOS"]==eos].sort_values("max_step", ascending=False)
    for obs, sty in obs_styles.items():
        ax1.plot(df_e["max_step"], df_e[obs], color=eos_to_color[eos], ls=sty["ls"], marker=sty["marker"], ms=5)
ax1.set_xscale("log")
ax1.invert_xaxis()
ax1.set_xlabel("Grid resolution proxy: max_step (smaller = finer)")
ax1.set_ylabel("Observable value (units as in Table)")
ax1.set_title("Panel A — Convergence ladder (representative observables)")

leg1 = ax1.legend(handles=eos_handles, title="EOS", loc="upper left", frameon=True)
ax1.add_artist(leg1)
ax1.legend(handles=obs_handles, title="Observable", loc="lower left", frameon=True)

inset = ax1.inset_axes([0.62,0.58,0.35,0.35])
inset.axis("off")
inset.text(0,1,"\n".join(lines), va="top")
inset.set_title("Estimated p", fontsize=9)

# Re-draw Panel B on ax2
ax2.axhspan(-0.10, 0.10, alpha=0.18)
ax2.axhspan( 0.10, 0.30, alpha=0.14)
ax2.axhspan(-0.30,-0.10, alpha=0.14)
ax2.axhspan( 0.30, 1.00, alpha=0.10)
ax2.axhspan(-1.00,-0.30, alpha=0.10)
for eos in eos_list:
    df = epsprof[epsprof["EOS"]==eos]
    ax2.plot(df["r_km"], df["epsratio"], lw=1.2, color=eos_to_color[eos], label=eos)
    m = float(np.max(np.abs(df["epsratio"].values)))
    r_anno = float(df["r_km"].max())*0.65
    eps_anno = float(df.loc[(df["r_km"]-r_anno).abs().idxmin(), "epsratio"])
    ax2.annotate(f"max|ε|={m:.2f}", xy=(r_anno, eps_anno), fontsize=8, color=eos_to_color[eos])
ax2.axhline(0, lw=0.8)
ax2.set_xlabel("Radius r (km)")
ax2.set_ylabel("epsratio(r)")
ax2.set_title("Panel B — Radial epsratio profiles with interpretability bands")
ylim = max(0.35, float(np.max(np.abs(epsprof["epsratio"].values)))*1.25)
ax2.set_ylim(-ylim, ylim)
ax2.legend(loc="upper right", frameon=True, fontsize=8)

# Re-draw Panel C on ax3
for status in status_order:
    df = scan[scan["obs_status"]==status]
    if len(df)==0:
        continue
    ax3.hist(df["delta_total_pct_plot"], bins=bins, alpha=0.6,
             label=status, color=status_colors.get(status,(0.2,0.2,0.2,0.55)))
ax3.set_xlabel(r"Total discretization error proxy $\delta_{\mathrm{total}}$ (%)")
ax3.set_ylabel("Frequency")
ax3.set_title("Panel C — Error distribution and automated classification")

ax3b = ax3.twinx()
ax3b.plot(vals, cum, lw=1.5, color="black")
ax3b.set_ylabel("Cumulative fraction")
ax3b.set_ylim(0, 1.0)

for thr in [20, 50]:
    ax3.axvline(thr, lw=1.0, ls="--", color="black")
    ax3.text(thr+1, ax3.get_ylim()[1]*0.9, f"{thr}%", fontsize=9)

ax3.legend(loc="upper right", frameon=True)

fig.suptitle("Figure X — Compact numerical stability overview", fontsize=14, y=0.98)
fig_path = os.path.join(OUT_FIG, "figX_numerical_stability_overview.png")
fig.savefig(fig_path, dpi=450, bbox_inches="tight")

print("Saved:")
print(" ", figA_path)
print(" ", figB_path)
print(" ", figC_path)
print(" ", fig_path)
