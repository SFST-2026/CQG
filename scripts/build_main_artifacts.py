#!/usr/bin/env python3
"""build_main_artifacts.py

One-command helper to (re)generate the core *main-text* artifacts that reviewers
usually look for:

  1) Λ_1.4(σ) figure for SLy/AP4 with a conservative observation band overlay.
  2) Ensure the Richardson triplet image exists (or warn if missing).

This script is intentionally lightweight and does not run expensive TOV jobs.
Use refine_and_retry_cli.py / targeted_rerun_outliers.py for stabilization runs.
"""

from __future__ import annotations

import subprocess
from pathlib import Path


def run(cmd: list[str]) -> None:
    print("$", " ".join(cmd))
    subprocess.check_call(cmd)


def main() -> None:
    # 1) Data-based Λ_1.4(σ) figure
    run(["python3", "scripts/make_lambda1p4_vs_sigma_obsband.py", "--eos", "SLy", "AP4"]) 

    # 2) Richardson triplet (already committed as an artifact; warn if missing)
    trip = Path("outputs/figures/richardson_triplet_main.png")
    if not trip.exists():
        print("WARNING: outputs/figures/richardson_triplet_main.png not found.\n"
              "If you have per-run richardson.png files under outputs/diagnostics/<run_id>/, "
              "generate a triplet collage or copy three representative plots into outputs/figures/.")
    else:
        print(f"Found Richardson triplet: {trip}")


if __name__ == "__main__":
    main()
