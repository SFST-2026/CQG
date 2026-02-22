#!/usr/bin/env python3
"""Generate per-run dossiers for excluded/diagnostic runs.

This script is a convenience layer to avoid manual documentation effort.
It scans a run index CSV (default: supplement/excluded_runs/index.csv) and,
for each run_id, creates a folder with:
  - diagnosis.txt (human-readable summary)
  - residual_trace.png (placeholder or copied if available)
  - epsratio_profile.png (placeholder or copied if available)

If your pipeline already writes artifacts under outputs/runs/<run_id>/,
the script will copy them when found.

Usage:
  python scripts/generate_excluded_run_dossiers.py \
      --index supplement/excluded_runs/index.csv \
      --runs-dir outputs/runs \
      --out-dir supplement/excluded_runs
"""
from __future__ import annotations
import argparse, csv, os, shutil
from pathlib import Path

DEFAULT_ARTIFACTS = {
    "residual_trace.png": ["residual_trace.png", "residual.png", "newton_residual.png"],
    "epsratio_profile.png": ["epsratio_profile.png", "epsratio.png"],
    "richardson.png": ["richardson.png", "convergence.png"]
}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--index", type=Path, default=Path("supplement/excluded_runs/index.csv"))
    ap.add_argument("--runs-dir", type=Path, default=Path("outputs/runs"))
    ap.add_argument("--out-dir", type=Path, default=Path("supplement/excluded_runs"))
    args = ap.parse_args()

    if not args.index.exists():
        raise SystemExit(f"Index not found: {args.index}")

    args.out_dir.mkdir(parents=True, exist_ok=True)

    with args.index.open(newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    for r in rows:
        run_id = r.get("run_id") or r.get("id") or ""
        if not run_id:
            continue
        reason = r.get("reason_code","").strip()
        eos = r.get("eos","").strip()
        sigma = r.get("sigma","").strip()
        eps = r.get("epsratio_max","").strip()
        status = r.get("status","excluded").strip()

        run_dir = args.runs_dir / run_id
        out_run = args.out_dir / run_id
        out_run.mkdir(parents=True, exist_ok=True)

        # diagnosis.txt
        diag = out_run / "diagnosis.txt"
        if not diag.exists():
            diag.write_text(
                f"""run_id: {run_id}
status: {status}
reason_code: {reason}
eos: {eos}
sigma: {sigma}
epsratio_max: {eps}

Notes:
- This dossier is auto-generated from the run index.
- If additional solver logs exist, place them under {run_dir} and re-run this script.
""")

        # copy artifacts if present; else leave placeholder text file
        for target, candidates in DEFAULT_ARTIFACTS.items():
            dst = out_run / target
            if dst.exists():
                continue
            src_found = None
            if run_dir.exists():
                for c in candidates:
                    cand = run_dir / c
                    if cand.exists():
                        src_found = cand
                        break
            if src_found:
                shutil.copy(src_found, dst)
            else:
                # create placeholder marker (so reviewers see file is expected)
                (out_run / (target + ".MISSING.txt")).write_text(
                    f"""Missing artifact: {target}

If available, place {target} (or an equivalent) under:
  {run_dir}/
and re-run:
  python scripts/generate_excluded_run_dossiers.py
""")

    print(f"Generated/updated dossiers for {len(rows)} runs in {args.out_dir}")

if __name__ == "__main__":
    main()
