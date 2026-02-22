#!/usr/bin/env python3
"""
collect_results.py
Collect per-run summary.json files under outputs/diagnostics/ and update:
 - outputs/scan_grid.csv
 - outputs/audit_index.csv

Designed to work with the refinement workflow (refine_and_retry_cli.py) and the run wrapper.
It is safe to run repeatedly (it rewrites the CSVs from the current filesystem state).

Usage:
    python3 scripts/collect_results.py
"""

from __future__ import annotations
import json
import csv
from pathlib import Path
from typing import Dict, Any, List, Optional

WORKDIR = Path.cwd()
DIAG = WORKDIR / "outputs" / "diagnostics"
OUT_SCAN = WORKDIR / "outputs" / "scan_grid.csv"
OUT_AUDIT = WORKDIR / "outputs" / "audit_index.csv"

EPS_ACCEPT = 0.10
EPS_STRESS = 0.30

def _safe_float(x) -> Optional[float]:
    try:
        if x is None or x == "":
            return None
        return float(x)
    except Exception:
        return None

def find_summaries(diag_dir: Path) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    if not diag_dir.exists():
        return rows
    for d in sorted(diag_dir.iterdir()):
        if not d.is_dir():
            continue
        s = d / "summary.json"
        if not s.exists():
            continue
        try:
            data = json.loads(s.read_text())
            # Ensure run_id defaults to directory name
            data.setdefault("run_id", d.name)
            data.setdefault("path", str(Path("outputs/diagnostics") / d.name))
            rows.append(data)
        except Exception:
            # ignore unreadable JSON but keep going
            continue
    return rows

def load_audit(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        return []
    with path.open(newline="") as f:
        return list(csv.DictReader(f))

def classify_status(converged: bool, max_epsratio: Optional[float]) -> str:
    if not converged:
        return "DIAGNOSTIC"
    if max_epsratio is None:
        return "DIAGNOSTIC"
    if max_epsratio <= EPS_ACCEPT:
        return "RESOLVED"
    if max_epsratio <= EPS_STRESS:
        return "STRESS_RESOLVED"
    return "DIAGNOSTIC"

def update_audit(existing: List[Dict[str, Any]], summaries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    # Keep any existing manual reasons, but refresh computed fields when summary exists.
    aud_map: Dict[str, Dict[str, Any]] = {}
    for r in existing:
        rid = r.get("run_id") or r.get("path") or ""
        if rid:
            aud_map[rid] = dict(r)

    for s in summaries:
        rid = str(s.get("run_id") or "")
        if not rid:
            continue
        converged = bool(s.get("converged", False))
        max_eps = _safe_float(s.get("max_epsratio"))
        status = classify_status(converged, max_eps)
        entry = aud_map.get(rid, {})
        entry.update({
            "run_id": rid,
            "eos": s.get("eos", ""),
            "sigma": s.get("sigma", ""),
            "status": status,
            "reason": entry.get("reason", ""),  # preserve if present
            "path": str(Path("outputs/diagnostics") / rid),
        })
        aud_map[rid] = entry

    return list(aud_map.values())

def write_csv(path: Path, rows: List[Dict[str, Any]], fieldnames: List[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in fieldnames})

def main() -> None:
    summaries = find_summaries(DIAG)

    # Write scan_grid.csv (wide; keep keys that appear frequently)
    if summaries:
        # union keys
        keys = set()
        for s in summaries:
            keys |= set(s.keys())
        # Stable ordering
        preferred = [
            "run_id","eos","variant","sigma","g","Gamma","seed",
            "converged","M_max","R_1p4","Lambda_1p4",
            "max_epsratio","wfaktor_max","newton_final_residual",
            "delta_total","status","path","error"
        ]
        fieldnames = [k for k in preferred if k in keys] + [k for k in sorted(keys) if k not in preferred]
        write_csv(OUT_SCAN, summaries, fieldnames)
    else:
        OUT_SCAN.write_text("")

    # Update audit_index.csv
    existing = load_audit(OUT_AUDIT)
    updated = update_audit(existing, summaries)
    audit_fields = ["run_id","eos","sigma","status","reason","path"]
    write_csv(OUT_AUDIT, updated, audit_fields)

    print(f"Wrote {OUT_SCAN} ({len(summaries)} summaries)")
    print(f"Wrote {OUT_AUDIT} ({len(updated)} audit rows)")

if __name__ == "__main__":
    main()
