#!/usr/bin/env python3
"""
Generate Figure X (3-panel numerical validation summary) using Matplotlib only.

Inputs (in --data-dir):
  - convergence.csv: columns [eos, observable, h, Q, Q_R, p_est, sigma]
  - epsratio_summary.csv: columns [run_id, eos, sigma, epsratio_max]
  - residual_traces.h5: HDF5 with groups per EOS containing:
        representative/iter, representative/residual
        ensemble/iter, ensemble/residuals  (shape: [n_traces, n_iter])

Outputs (in --out-dir):
  - figX_panelA_convergence.pdf/png
  - figX_panelB_epsratio.pdf/png
  - figX_panelC_residuals.pdf/png
  - figX_3panel.pdf/png
Also writes:
  - plot_metadata.json (copy of template with actual timestamp + resolved file paths)
"""
from __future__ import annotations
import argparse, json, datetime
from pathlib import Path
import numpy as np
import pandas as pd
import h5py
import matplotlib.pyplot as plt

def write_metadata(out_dir: Path, meta_template_path: Path, resolved_files: list[str], cmd: str) -> None:
    if meta_template_path.exists():
        meta = json.loads(meta_template_path.read_text(encoding="utf-8"))
    else:
        meta = {}
    meta["generated_at_utc"] = datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
    meta["data_files_used"] = resolved_files
    meta["command"] = cmd
    (out_dir / "plot_metadata.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")

def panelA_convergence(df: pd.DataFrame, observable: str, out_dir: Path, dpi: int) -> None:
    sub = df[df["observable"] == observable].copy()
    if sub.empty:
        raise ValueError(f"No rows for observable={observable} in convergence.csv")
    fig, ax = plt.subplots(figsize=(7.0, 3.2))
    for eos, g in sub.groupby("eos"):
        g = g.sort_values("h", ascending=False)
        ax.plot(g["h"], g["Q"], marker="o", label=f"{eos} raw")
        # Richardson extrapolated as horizontal dashed line at Q_R
        qR = float(g["Q_R"].iloc[0])
        ax.hlines(qR, xmin=g["h"].min(), xmax=g["h"].max(), linestyles="--")
        # uncertainty band: use max(|Q-Q_R|) at finest grid as crude example
        finest = g.sort_values("h").iloc[0]
        err = abs(float(finest["Q"]) - qR)
        ax.fill_between([g["h"].min(), g["h"].max()], [qR-err, qR-err], [qR+err, qR+err], alpha=0.15)
        # annotate p
        p_est = float(g["p_est"].iloc[0])
        ax.annotate(f"{eos}: p≈{p_est:.2f}", xy=(g["h"].iloc[-1], g["Q"].iloc[-1]),
                    xytext=(5,5), textcoords="offset points", fontsize=8)
    ax.set_xlabel("Resolution level h")
    ax.set_ylabel(f"Q ({observable})")
    ax.set_xscale("log")
    ax.invert_xaxis()  # finer to the right if desired; invert to show convergence with decreasing h
    ax.legend(fontsize=8, ncol=2)
    ax.set_title("Panel A: Convergence ladder (Richardson)")
    fig.tight_layout()
    for ext in ["pdf", "png"]:
        fig.savefig(out_dir / f"figX_panelA_convergence.{ext}", dpi=(dpi if ext.lower() in {'png','tif','tiff'} else None))
    plt.close(fig)

def panelB_epsratio(df: pd.DataFrame, out_dir: Path, dpi: int, thr1: float=0.10, thr2: float=0.30) -> None:
    vals = df["epsratio_max"].to_numpy()
    fig, ax = plt.subplots(figsize=(7.0, 3.2))
    ax.hist(vals, bins=30, density=True, alpha=0.8)
    ax.axvline(thr1, linestyle="--")
    ax.axvline(thr2, linestyle="--")
    ax.set_xlim(0, 0.5)
    ax.set_xlabel(r"$\max_r |\mathrm{epsratio}(r)|$")
    ax.set_ylabel("Density")
    med = float(np.median(vals))
    p10, p90 = np.quantile(vals, [0.1, 0.9])
    frac = float(np.mean(vals <= thr1))
    txt = f"median={med:.3f}\n10–90%={p10:.3f}–{p90:.3f}\nfrac≤{thr1:.2f}={frac:.2%}"
    ax.text(0.98, 0.95, txt, transform=ax.transAxes, ha="right", va="top", fontsize=8,
            bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8))
    ax.set_title("Panel B: epsratio distribution")
    fig.tight_layout()
    for ext in ["pdf", "png"]:
        fig.savefig(out_dir / f"figX_panelB_epsratio.{ext}", dpi=(dpi if ext.lower() in {'png','tif','tiff'} else None))
    plt.close(fig)

def panelC_residuals(h5_path: Path, out_dir: Path, dpi: int) -> None:
    fig, ax = plt.subplots(figsize=(7.0, 3.2))
    with h5py.File(h5_path, "r") as f:
        for eos in f.keys():
            grp = f[eos]
            it = grp["representative/iter"][()]
            resid = grp["representative/residual"][()]
            ax.plot(it, resid, label=f"{eos} representative")
            ens_it = grp["ensemble/iter"][()]
            ens_res = grp["ensemble/residuals"][()]
            # plot a few thin grey ensemble traces
            for k in range(min(ens_res.shape[0], 5)):
                ax.plot(ens_it, ens_res[k], color="0.7", linewidth=1, alpha=0.6)
    ax.set_yscale("log")
    ax.set_xlabel("Newton iteration")
    ax.set_ylabel("Residual norm")
    ax.set_title("Panel C: Solver residual trace")
    ax.legend(fontsize=8)
    fig.tight_layout()
    for ext in ["pdf", "png"]:
        fig.savefig(out_dir / f"figX_panelC_residuals.{ext}", dpi=(dpi if ext.lower() in {'png','tif','tiff'} else None))
    plt.close(fig)

def combine_panels(out_dir: Path, dpi: int) -> None:
    # Read the saved PNGs and combine into one 3-panel figure
    import matplotlib.image as mpimg
    paths = [out_dir/"figX_panelA_convergence.png",
             out_dir/"figX_panelB_epsratio.png",
             out_dir/"figX_panelC_residuals.png"]
    imgs = [mpimg.imread(p) for p in paths]
    fig, axes = plt.subplots(3, 1, figsize=(7.2, 9.6))
    for ax, img, label in zip(axes, imgs, ["A","B","C"]):
        ax.imshow(img)
        ax.axis("off")
        ax.text(0.01, 0.98, label, transform=ax.transAxes, ha="left", va="top", fontsize=14)
    fig.tight_layout()
    for ext in ["pdf", "png"]:
        fig.savefig(out_dir / f"figX_3panel.{ext}", dpi=(dpi if ext.lower() in {'png','tif','tiff'} else None))
    plt.close(fig)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", type=Path, required=True, help="Directory containing input data files")
    ap.add_argument("--dpi", type=int, default=600, help="DPI for raster outputs (png/tiff); vector PDFs ignore dpi.")
    ap.add_argument("--out-dir", type=Path, required=True, help="Output directory for figures")
    ap.add_argument("--observable", type=str, default="Lambda14", help="Observable key used in convergence.csv")
    ap.add_argument("--emit-panels-only", action="store_true",
                    help="If set, only write the three individual panels and skip the combined 3-panel montage.")
    ap.add_argument("--meta-template", type=Path, default=Path("plot_metadata.json.template"),
                    help="Path to plot metadata template (defaults to repo root template)")
    args = ap.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    conv_path = args.data_dir / "convergence.csv"
    eps_path = args.data_dir / "epsratio_summary.csv"
    h5_path  = args.data_dir / "residual_traces.h5"

    conv = pd.read_csv(conv_path)
    eps = pd.read_csv(eps_path)

    panelA_convergence(conv, args.observable, args.out_dir, args.dpi)
    panelB_epsratio(eps, args.out_dir, args.dpi)
    panelC_residuals(h5_path, args.out_dir, args.dpi)
    if not args.emit_panels_only:
        combine_panels(args.out_dir, args.dpi)

    cmd = " ".join([str(x) for x in [
        "python", "scripts/plot_figureX.py",
        "--data-dir", args.data_dir,
        "--out-dir", args.out_dir,
        "--observable", args.observable
    ]])
    resolved = [str(conv_path), str(eps_path), str(h5_path)]
    # meta-template may be relative; if not found, ignore
    mt = args.meta_template if args.meta_template.is_absolute() else (Path.cwd()/args.meta_template)
    write_metadata(args.out_dir, mt, resolved, cmd)

if __name__ == "__main__":
    main()