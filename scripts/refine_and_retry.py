#!/usr/bin/env python3
"""refine_and_retry.py

Automated refinement/retry controller for diagnostic runs.

Reads targets from outputs/audit_index.csv (default) and for each run attempts
up to N retries with progressively stronger numerical settings:
- grid refinement via extra['grid_factor']
- Newton solver tolerance via extra['newton_tol']

Each attempt is logged to:
  outputs/diagnostics/<orig_run_id>/refinement_log.json

This script is designed to work with scan_wrappers.compute_tov_case.

Usage:
  python scripts/refine_and_retry.py --input outputs/audit_index.csv --n-retries 3

Notes:
- compute_tov_case must accept extra fields 'grid_factor' and 'newton_tol' and pass
  them into the solver configuration (e.g., N_radial = int(N_base*grid_factor)).
- If you prefer CLI/Slurm submission, use scripts/refine_and_retry_cli.py.
"""

import argparse
import csv
import json
import time
from pathlib import Path

GRID_FACTORS = [1.5, 2.0, 3.0]
NEWTON_TOLS  = [1e-6, 1e-7, 1e-8]
EPS_ACCEPT   = 0.10
EPS_STRESS   = 0.30
SLEEP_BETWEEN = 1.0

WORKDIR = Path.cwd()
DIAG_BASE = WORKDIR / "outputs" / "diagnostics"
AUDIT_INDEX = WORKDIR / "outputs" / "audit_index.csv"

def load_audit_rows(path: Path):
    if not path.exists():
        return []
    with open(path, newline="") as f:
        return list(csv.DictReader(f))

def append_refinement_log(orig_run_id: str, entry: dict):
    p = DIAG_BASE / orig_run_id / "refinement_log.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    data = []
    if p.exists():
        try:
            data = json.load(open(p))
        except Exception:
            data = []
    data.append(entry)
    json.dump(data, open(p, "w"), indent=2)

def run_local_compute(eos: str, sigma: float, run_tag: str, extra: dict, grid_factor: float, newton_tol: float, timeout: int):
    from scan_wrappers import compute_tov_case
    ex = dict(extra or {})
    ex.update({"grid_factor": grid_factor, "newton_tol": newton_tol})
    return compute_tov_case(eos=eos, sigma=sigma, run_tag=run_tag, extra=ex, timeout=timeout)

def main(args):
    rows = load_audit_rows(Path(args.input))
    targets = [r for r in rows if r.get("status","").upper() in ("DIAGNOSTIC","FAILED","PARSE_ERROR")]
    print(f"Found {len(targets)} diagnostic/failed runs.")
    for r in targets:
        orig_run_id = r.get("run_id") or Path(r.get("path","")).name
        eos = r.get("eos") or "UNKNOWN"
        sigma = float(r.get("sigma") or 0.0)

        # read original metadata extra if available
        extra = {}
        meta_path = DIAG_BASE / orig_run_id / "metadata.json"
        if meta_path.exists():
            try:
                meta = json.load(open(meta_path))
                extra = meta.get("extra", {}) or {}
            except Exception:
                extra = {}

        resolved = False
        for attempt in range(min(args.n_retries, len(GRID_FACTORS))):
            gf = GRID_FACTORS[attempt]
            nt = NEWTON_TOLS[min(attempt, len(NEWTON_TOLS)-1)]
            run_tag = f"{orig_run_id}_ref{attempt+1}_gf{gf}_nt{nt}"
            print(f"[{orig_run_id}] attempt {attempt+1}/{args.n_retries}: gf={gf}, nt={nt}")
            ts = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            try:
                res = run_local_compute(eos=eos, sigma=sigma, run_tag=run_tag, extra=extra, grid_factor=gf, newton_tol=nt, timeout=args.timeout)
            except Exception as e:
                append_refinement_log(orig_run_id, {"timestamp": ts, "status":"REFINE_FAILED", "attempt":attempt+1, "grid_factor":gf, "newton_tol":nt, "error":str(e)})
                time.sleep(SLEEP_BETWEEN)
                continue

            converged = bool(res.get("converged", False))
            max_eps = res.get("max_epsratio", None)
            append_refinement_log(orig_run_id, {"timestamp": ts, "status":"ATTEMPT_RESULT", "attempt":attempt+1, "grid_factor":gf, "newton_tol":nt, "run_tag":run_tag, "converged":converged, "max_epsratio":max_eps})

            if converged and max_eps is not None and float(max_eps) <= EPS_ACCEPT:
                append_refinement_log(orig_run_id, {"timestamp": ts, "status":"RESOLVED", "note":f"epsratio={max_eps}", "run_tag":run_tag})
                resolved = True
                break
            if converged and max_eps is not None and float(max_eps) <= EPS_STRESS:
                append_refinement_log(orig_run_id, {"timestamp": ts, "status":"STRESS_RESOLVED", "note":f"epsratio={max_eps}", "run_tag":run_tag})
                resolved = True
                break

            time.sleep(SLEEP_BETWEEN)

        if not resolved:
            ts = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            append_refinement_log(orig_run_id, {"timestamp": ts, "status":"UNRESOLVED", "note":"exhausted retries; keep diagnostic/exclude per policy"})

    print("Done.")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default=str(AUDIT_INDEX))
    ap.add_argument("--n-retries", type=int, default=3)
    ap.add_argument("--timeout", type=int, default=3600)
    args = ap.parse_args()
    main(args)
