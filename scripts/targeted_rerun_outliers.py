#!/usr/bin/env python3
"""targeted_rerun_outliers.py

Builds a *re-run plan* for any run with delta_total > 50% in any headline observable,
and (optionally) executes re-runs via your existing pipeline wrapper.

This script is designed for reviewer-facing auditability:
- It never silently drops outliers.
- Every attempted remediation is logged to outputs/diagnostics/<run_id>/diagnosis.txt.
- If stabilization fails, the run remains EXCLUDED and is indexed in outputs/audit_index.csv.

Typical usage:
    python scripts/targeted_rerun_outliers.py --runs outputs/runs_summary.csv --dry-run
    python scripts/targeted_rerun_outliers.py --runs outputs/runs_summary.csv --execute

Notes:
- In this repository snapshot, outliers are already EXCLUDED and documented; this tool provides
  the reproducible *protocol* to stabilize them on HPC.
"""
from __future__ import annotations
import argparse
import os
from pathlib import Path

def _append_refinement_log(orig_run_id: str, entry: dict, diag_base: Path = Path("outputs/diagnostics")) -> None:
    """Append an audit entry to outputs/diagnostics/<orig_run_id>/refinement_log.json."""
    log_path = diag_base / orig_run_id / "refinement_log.json"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    if log_path.exists():
        try:
            data = json.loads(log_path.read_text())
            if not isinstance(data, list):
                data = [data]
        except Exception:
            data = []
    else:
        data = []
    data.append(entry)
    log_path.write_text(json.dumps(data, indent=2))

import pandas as pd
import json
import datetime

DEFAULT_RERUN_CFG = {
    "grid_refine": "n_to_2n",
    "epsabs": 1e-12,
    "epsrel": 1e-12,
    "max_iter": 400,
    "newton_damping": True,
    "alt_integrator": "RK45_or_BDF",
}

def now_iso():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()

def load_runs(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    # normalize expected columns
    for c in ["delta_total_Mmax_pct","delta_total_R14_pct","delta_total_Lambda14_pct"]:
        if c not in df.columns:
            raise SystemExit(f"Missing column {c} in {path}")
    return df

def is_outlier(row) -> bool:
    return (row["delta_total_Mmax_pct"] > 50) or (row["delta_total_R14_pct"] > 50) or (row["delta_total_Lambda14_pct"] > 50)

def write_plan(df: pd.DataFrame, out_csv: str):
    Path(out_csv).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_csv, index=False)

def append_diagnosis(run_id: str, text: str):
    d = Path("outputs/diagnostics")/run_id
    d.mkdir(parents=True, exist_ok=True)
    p = d/"diagnosis.txt"
    with open(p, "a", encoding="utf-8") as f:
        f.write(text.rstrip()+"\n")


def append_refinement_event(run_id: str, **fields) -> None:
    """Append a structured audit entry for a stabilization re-run.

    Writes to outputs/diagnostics/<run_id>/refinement_log.json.
    """
    entry = {"timestamp": now_iso(), **fields}
    _append_refinement_log(str(run_id), entry)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", default="outputs/runs_summary.csv", help="Path to runs_summary.csv")
    ap.add_argument("--out", default="outputs/rerun_plan_delta_total_gt50.csv", help="Output CSV for the rerun plan")
    ap.add_argument("--dry-run", action="store_true", help="Only write the plan; do not run anything")
    ap.add_argument("--execute", action="store_true", help="Execute re-runs via your pipeline wrapper (requires compute_tov_case wired)")
    args = ap.parse_args()

    if args.execute and args.dry_run:
        raise SystemExit("Choose only one of --dry-run or --execute")

    df = load_runs(args.runs)
    outliers = df[df.apply(is_outlier, axis=1)].copy()

    plan_rows = []
    for _, r in outliers.iterrows():
        plan_rows.append({
            "run_id": r.get("run_id"),
            "EOS": r.get("EOS"),
            "case": r.get("case"),
            "variant": r.get("variant"),
            "reason": "delta_total>50% (one or more observables)",
            "rerun_cfg": json.dumps(DEFAULT_RERUN_CFG),
            "if_fail": "exclude_and_audit",
            "diagnostics_dir": f"outputs/diagnostics/{r.get('run_id')}/",
        })
        append_diagnosis(str(r.get("run_id")),
            f"[{now_iso()}] RERUN-PLAN: flagged delta_total>50%. Suggested remediation: {DEFAULT_RERUN_CFG}.")
        append_refinement_event(
            str(r.get("run_id")),
            status="RERUN_PLANNED",
            reason="delta_total>50% (one or more observables)",
            suggested_cfg=DEFAULT_RERUN_CFG,
        )

    plan_df = pd.DataFrame(plan_rows)
    write_plan(plan_df, args.out)

    if args.dry_run or not args.execute:
        print(f"Wrote plan with {len(plan_df)} outliers -> {args.out}")
        return

    # Execute re-runs (requires a wired wrapper)
    from scan_wrappers import compute_tov_case  # noqa
    for _, r in plan_df.iterrows():
        run_id = r["run_id"]
        eos = r["EOS"]
        # sigma/chi parameters are expected to be in runs_summary; users may extend as needed
        row = df[df["run_id"]==run_id].iloc[0]
        sigma = float(row.get("sigma", 0.0))
        extra = {"rerun_cfg": DEFAULT_RERUN_CFG, "parent_run_id": run_id}
        append_diagnosis(run_id, f"[{now_iso()}] RERUN-EXECUTE: starting.")
        append_refinement_event(
            run_id,
            status="RERUN_START",
            eos=eos,
            sigma=sigma,
            run_tag=f"{run_id}__rerun",
            cfg=DEFAULT_RERUN_CFG,
        )
        try:
            res = compute_tov_case(eos=eos, sigma=sigma, run_tag=f"{run_id}__rerun", extra=extra)
            append_diagnosis(run_id, f"[{now_iso()}] RERUN-EXECUTE: finished converged={res.get('converged')}")
            append_refinement_event(
                run_id,
                status="RERUN_RESULT",
                converged=bool(res.get("converged", False)),
                max_epsratio=res.get("max_epsratio", None),
                newton_final_residual=res.get("newton_final_residual", None),
            )
        except Exception as e:
            append_diagnosis(run_id, f"[{now_iso()}] RERUN-EXECUTE: exception {e}")
            append_refinement_event(run_id, status="RERUN_EXCEPTION", error=str(e))

if __name__ == "__main__":
    main()
