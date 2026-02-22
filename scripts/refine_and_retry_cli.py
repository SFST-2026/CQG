#!/usr/bin/env python3
"""refine_and_retry_cli.py

Automated refinement/retry controller for diagnostic runs.

Modes:
  - backend=wrapper (default): calls `scan_wrappers.compute_tov_case` directly.
  - backend=cli: calls an external solver via TOV_CLI_TEMPLATE.

Usage:
  python scripts/refine_and_retry_cli.py --input outputs/audit_index.csv --mode local --backend wrapper --limit 10
  python scripts/refine_and_retry_cli.py --input outputs/audit_index.csv --mode slurm --backend cli

This script appends an auditable log to:
  outputs/diagnostics/<orig_run_id>/refinement_log.json
"""

from __future__ import annotations
import argparse
import csv
import json
import os
import shlex
import subprocess
import time
from pathlib import Path
import sys
REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
from typing import Dict, Any, Optional, List

WORKDIR = Path.cwd()
DIAG_BASE = WORKDIR / "outputs" / "diagnostics"

# External CLI template (backend=cli). Replace with your real entrypoint.
TOV_CLI_TEMPLATE = (
    "python run_tov.py --eos {EOS} --sigma {SIGMA} --run-tag {RUN_TAG} "
    "--grid-factor {GRID_FACTOR} --newton-tol {NEWTON_TOL}"
)

# Optional Slurm submission template (mode=slurm, backend=cli)
SLURM_SCRIPT = WORKDIR / "slurm" / "run_refined.sbatch"
SLURM_SUBMIT_TEMPLATE = "sbatch {SLURM_SCRIPT} {EOS} {SIGMA} {RUN_ID} {GRID_FACTOR} {NEWTON_TOL}"

GRID_FACTORS_DEFAULT = [1.5, 2.0, 3.0]
NEWTON_TOLS_DEFAULT = [1e-6, 1e-7, 1e-8]

EPS_ACCEPT = 0.10
EPS_STRESS = 0.30
DELTA_TOTAL_ACCEPT = 50.0  # percent

def _utc() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

def load_audit_rows(path: Path) -> List[Dict[str,str]]:
    if not path.exists():
        return []
    with open(path, newline="") as f:
        return list(csv.DictReader(f))

def write_refinement_log(orig_run_id: str, entry: Dict[str, Any]) -> None:
    p = DIAG_BASE / orig_run_id / "refinement_log.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    if p.exists():
        data = json.loads(p.read_text())
    else:
        data = []
    data.append(entry)
    p.write_text(json.dumps(data, indent=2))

def parse_summary(run_dir: Path) -> Optional[Dict[str, Any]]:
    p = run_dir / "summary.json"
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text())
    except Exception:
        return None

def run_cli(cmd: str, cwd: Path, timeout: int) -> Dict[str, Any]:
    try:
        proc = subprocess.run(shlex.split(cmd), cwd=str(cwd), capture_output=True, text=True, timeout=timeout)
        return {"returncode": proc.returncode, "stdout": proc.stdout, "stderr": proc.stderr}
    except subprocess.TimeoutExpired as e:
        return {"returncode": -1, "stdout": "", "stderr": f"timeout: {e}"}

def attempt_wrapper(eos: str, sigma: float, run_tag: str, extra: Dict[str, Any], grid_factor: float, newton_tol: float, timeout: int) -> Path:
    # Ensure deterministic lightweight dummy runs unless user wired the real solver.
    os.environ.setdefault("SFST_DUMMY", "1")
    from scan_wrappers import compute_tov_case
    extra = dict(extra or {})
    extra.update({"grid_factor": grid_factor, "newton_tol": newton_tol})
    res = compute_tov_case(eos=eos, sigma=float(sigma), run_tag=run_tag, extra=extra, timeout=timeout)
    run_dir = DIAG_BASE / run_tag
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "summary.json").write_text(json.dumps(res, indent=2))
    return run_dir

def attempt_cli(eos: str, sigma: float, run_tag: str, grid_factor: float, newton_tol: float, timeout: int) -> Path:
    cmd = TOV_CLI_TEMPLATE.format(EOS=shlex.quote(eos), SIGMA=sigma, RUN_TAG=shlex.quote(run_tag), GRID_FACTOR=grid_factor, NEWTON_TOL=newton_tol)
    run_dir = DIAG_BASE / run_tag
    run_dir.mkdir(parents=True, exist_ok=True)
    r = run_cli(cmd, WORKDIR, timeout=timeout)
    (run_dir / "run.log").write_text(r.get("stdout","") + "\n\nSTDERR:\n" + r.get("stderr",""))
    return run_dir

def is_resolved(summary: Dict[str, Any]) -> str:
    converged = bool(summary.get("converged", False))
    max_eps = summary.get("max_epsratio", None)
    delta_total = summary.get("delta_total_max_pct", None)
    if not converged:
        return "UNRESOLVED"
    if max_eps is not None and float(max_eps) > EPS_STRESS:
        return "UNRESOLVED"
    if delta_total is not None and float(delta_total) > DELTA_TOTAL_ACCEPT:
        return "UNRESOLVED"
    if max_eps is not None and float(max_eps) > EPS_ACCEPT:
        return "STRESS_RESOLVED"
    return "RESOLVED"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default="outputs/audit_index.csv")
    ap.add_argument("--mode", choices=["local","slurm"], default="local")
    ap.add_argument("--backend", choices=["wrapper","cli"], default="wrapper")
    ap.add_argument("--n_retries", type=int, default=3)
    ap.add_argument("--timeout", type=int, default=3600)
    ap.add_argument("--limit", type=int, default=0, help="limit number of target runs (0=all)")
    args = ap.parse_args()

    rows = load_audit_rows(Path(args.input))
    targets = [r for r in rows if r.get("status","").upper() in ("DIAGNOSTIC","FAILED","PARSE_ERROR","EXCLUDED")]
    if args.limit and len(targets) > args.limit:
        targets = targets[:args.limit]
    print(f"Found {len(targets)} target runs in {args.input}.")

    grid_factors = GRID_FACTORS_DEFAULT[:args.n_retries]
    newton_tols = NEWTON_TOLS_DEFAULT[:args.n_retries]

    for r in targets:
        orig_run_id = r.get("run_id") or Path(r.get("path","")).name
        eos = r.get("eos") or "UNKNOWN"
        try:
            sigma = float(r.get("sigma") or 0.0)
        except Exception:
            sigma = 0.0
        extra = {}
        # load extra from metadata.json if present
        meta = DIAG_BASE / orig_run_id / "metadata.json"
        if meta.exists():
            try:
                extra = json.loads(meta.read_text()).get("extra", {})
            except Exception:
                extra = {}

        write_refinement_log(orig_run_id, {"timestamp": _utc(), "status": "START", "eos": eos, "sigma": sigma})

        resolved_state = "UNRESOLVED"
        for i,(gf,nt) in enumerate(zip(grid_factors, newton_tols), start=1):
            run_tag = f"{orig_run_id}_ref{i}_gf{gf}_nt{nt}"
            write_refinement_log(orig_run_id, {"timestamp": _utc(), "status": "ATTEMPT_START", "attempt": i, "run_tag": run_tag, "grid_factor": gf, "newton_tol": nt, "backend": args.backend})

            if args.mode == "slurm":
                # For slurm mode we only submit (backend=cli). Users can adapt the template.
                cmd = SLURM_SUBMIT_TEMPLATE.format(SLURM_SCRIPT=str(SLURM_SCRIPT), EOS=eos, SIGMA=sigma, RUN_ID=orig_run_id, GRID_FACTOR=gf, NEWTON_TOL=nt)
                rsub = run_cli(cmd, WORKDIR, timeout=60)
                write_refinement_log(orig_run_id, {"timestamp": _utc(), "status": "SLURM_SUBMITTED", "attempt": i, "run_tag": run_tag, "returncode": rsub["returncode"], "stderr": rsub.get("stderr","")[:500]})
                continue

            # local execution
            if args.backend == "wrapper":
                run_dir = attempt_wrapper(eos=eos, sigma=sigma, run_tag=run_tag, extra=extra, grid_factor=gf, newton_tol=nt, timeout=args.timeout)
            else:
                run_dir = attempt_cli(eos=eos, sigma=sigma, run_tag=run_tag, grid_factor=gf, newton_tol=nt, timeout=args.timeout)

            summary = parse_summary(run_dir)
            if summary is None:
                write_refinement_log(orig_run_id, {"timestamp": _utc(), "status": "ATTEMPT_NO_SUMMARY", "attempt": i, "run_tag": run_tag})
                continue

            state = is_resolved(summary)
            write_refinement_log(orig_run_id, {"timestamp": _utc(), "status": "ATTEMPT_RESULT", "attempt": i, "run_tag": run_tag,
                                              "converged": bool(summary.get("converged", False)),
                                              "max_epsratio": summary.get("max_epsratio", None),
                                              "delta_total_max_pct": summary.get("delta_total_max_pct", None),
                                              "state": state})
            if state in ("RESOLVED","STRESS_RESOLVED"):
                resolved_state = state
                break

        write_refinement_log(orig_run_id, {"timestamp": _utc(), "status": "END", "final_state": resolved_state})

    print("Refinement loop complete.")

if __name__ == "__main__":
    main()