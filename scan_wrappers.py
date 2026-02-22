"""scan_wrappers.py

Compute wrapper templates for driving the existing TOV pipeline from parameter scans.

This file intentionally ships as a *template*. You should connect `_call_tov_entrypoint`
to your existing CLI / Makefile / Python entrypoint that performs a single TOV run
and writes `summary.json` plus diagnostics into the provided run directory.

Expected per-run directory:
  outputs/diagnostics/<run_id>/
    - summary.json              (required)
    - run.log                   (recommended: stdout/stderr)
    - metadata.json             (written by wrapper)
    - run_config.json           (written by wrapper)
    - diagnosis.txt/json        (written on failure)
    - richardson.png            (optional)
    - residuals.png             (optional)
    - wfaktor.png               (optional)

The scan controller (e.g. scripts/scan_mapping_sigma_g2_over_Gamma.py) expects
compute_tov_case(...) to return a standardized dict.
"""

from __future__ import annotations

import hashlib
import json
import os
import time
import subprocess
from pathlib import Path
from typing import Any, Dict, Optional

# --- Configuration defaults (adjust to your repo / cluster) ---
OUTPUT_BASE = Path("outputs/diagnostics")
DEFAULT_TIMEOUT = 60 * 60  # seconds per run
ENV_OVERRIDES = {
    "OMP_NUM_THREADS": "1",
    "MKL_NUM_THREADS": "1",
    "OPENBLAS_NUM_THREADS": "1",
    "NUMEXPR_NUM_THREADS": "1",
}

def _write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, sort_keys=True)

def make_run_id(eos: str, sigma: float, extra: Dict[str, Any]) -> str:
    """Create a unique, auditable run_id."""
    stamp = time.strftime("%Y%m%dT%H%M%S")
    payload = f"{eos}|{sigma}|{stamp}|{json.dumps(extra, sort_keys=True, default=str)}"
    run_hash = hashlib.sha256(payload.encode("utf-8")).hexdigest()[:10]
    return f"{eos}_{run_hash}_{stamp}"

def _call_tov_entrypoint(config_path: Path, run_dir: Path, env: Dict[str, str], timeout: int) -> int:
    """Hook to your actual TOV runner.

    Replace the placeholder command below with your actual pipeline call.
    The runner MUST write `summary.json` into run_dir on success.

    Examples:
      - subprocess.run(["./run_tov.sh", "--config", str(config_path)], cwd=repo_root, ...)
      - subprocess.run(["python", "-m", "sfst.run_one", str(config_path)], cwd=repo_root, ...)
    """
    # --- TEMPLATE HOOK ---
    # By default this function raises until you wire it to your pipeline.
    # For repository smoke tests / CI, you can set SFST_DUMMY=1 to generate a
    # deterministic placeholder summary.json without running the expensive solver.
    import os, json
    from pathlib import Path
    if os.environ.get("SFST_DUMMY", "0") == "1":
        # Deterministic, lightweight placeholder: mark as not converged so it never
        # contaminates headline results; still produces an auditable summary.json.
        summary = {
            "converged": False,
            "M_max": None,
            "R_1p4": None,
            "Lambda_1p4": None,
            "max_epsratio": 9.99,
            "wfaktor_max": None,
            "newton_final_residual": None,
            "delta_total_max_pct": 1.0e9,
            "note": "SFST_DUMMY=1 placeholder (wire _call_tov_entrypoint to your solver for real runs)."
        }
        Path(run_dir, "summary.json").write_text(json.dumps(summary, indent=2))
        return 0

    raise NotImplementedError(
        "Connect _call_tov_entrypoint(...) to your TOV pipeline so that it writes summary.json. "
        "For smoke tests only, set SFST_DUMMY=1 to generate a placeholder summary.json."
    )

def compute_tov_case(
    eos: str,
    sigma: float,
    run_tag: Optional[str] = None,
    extra: Optional[Dict[str, Any]] = None,
    timeout: int = DEFAULT_TIMEOUT,
) -> Dict[str, Any]:
    """Run one EOS/sigma point through the TOV pipeline and return a standardized result dict."""
    extra = extra or {}
    run_id = run_tag or make_run_id(eos, sigma, extra)

    run_dir = OUTPUT_BASE / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    # Metadata for reproducibility
    metadata = {
        "run_id": run_id,
        "eos": eos,
        "sigma": float(sigma),
        "extra": extra,
        "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    _write_json(run_dir / "metadata.json", metadata)

    # Deterministic environment
    env = dict(os.environ)
    env.update(ENV_OVERRIDES)
    env["SFST_SEED"] = str(extra.get("seed", 123456789))

    # Minimal config passed to your pipeline (extend as needed)
    config = {
        "eos": eos,
        "sigma": float(sigma),
        "seed": int(env["SFST_SEED"]),
        "output_dir": str(run_dir),
        **({"extra": extra} if extra else {}),
    }
    _write_json(run_dir / "run_config.json", config)

    # Run solver and capture logs
    # Run solver and capture logs
    try:
        log_path = run_dir / "run.log"
        with open(log_path, "wb") as logf:
            # If you implement _call_tov_entrypoint using subprocess.run,
            # redirect stdout/stderr into logf there, or do it here.
            exit_code = _call_tov_entrypoint(
                config_path=run_dir / "run_config.json",
                run_dir=run_dir,
                env=env,
                timeout=timeout,
            )
            # If your call function does not write into logf, remove this block.
            # (Keeping logf open ensures it exists for auditing.)
        # Record exit code
        _write_json(run_dir / "provenance.json", {"exit_code": exit_code})
    except Exception as e:
        (run_dir / "diagnosis.txt").write_text(
            f"ERROR: {type(e).__name__}: {e}\n",
            encoding="utf-8"
        )
        _write_json(run_dir / "diagnosis.json", {"error": str(e), "type": type(e).__name__})
        return {
            "run_id": run_id,
            "sigma": float(sigma),
            "eos": eos,
            "converged": False,
            "error": str(e),
            "M_max": None,
            "R_1p4": None,
            "Lambda_1p4": None,
            "max_epsratio": None,
            "wfaktor_max": None,
            "newton_final_residual": None,
        }

    summary_path = run_dir / "summary.json"
    if not summary_path.exists():
        (run_dir / "diagnosis.txt").write_text(
            "ERROR: summary.json missing (pipeline did not produce expected output).\n",
            encoding="utf-8"
        )
        _write_json(run_dir / "diagnosis.json", {"error": "summary.json missing"})
        return {
            "run_id": run_id,
            "sigma": float(sigma),
            "eos": eos,
            "converged": False,
            "error": "summary.json missing",
            "M_max": None,
            "R_1p4": None,
            "Lambda_1p4": None,
            "max_epsratio": None,
            "wfaktor_max": None,
            "newton_final_residual": None,
        }

    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    result = {
        "run_id": run_id,
        "sigma": float(sigma),
        "eos": eos,
        "M_max": float(summary.get("M_max")) if summary.get("M_max") is not None else None,
        "R_1p4": float(summary.get("R_1p4")) if summary.get("R_1p4") is not None else None,
        "Lambda_1p4": float(summary.get("Lambda_1p4")) if summary.get("Lambda_1p4") is not None else None,
        "max_epsratio": float(summary.get("max_epsratio")) if summary.get("max_epsratio") is not None else None,
        "wfaktor_max": float(summary.get("wfaktor_max")) if summary.get("wfaktor_max") is not None else None,
        "newton_final_residual": float(summary.get("newton_final_residual")) if summary.get("newton_final_residual") is not None else None,
        "converged": bool(summary.get("converged", False)),
    }

    _write_json(run_dir / "run_index.json", {"status": "done", **result})
    return result


# NOTE: compute_tov_case passes extra['grid_factor'] and extra['newton_tol'] into run_config.json.
