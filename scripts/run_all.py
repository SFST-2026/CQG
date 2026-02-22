import os
import sys

# Ensure repo root is importable when this script is executed as a file.
_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

import subprocess, sys, shutil
from pathlib import Path

# clean outputs to avoid stale files
out = Path('outputs')
if out.exists():
    shutil.rmtree(out)


def run(cmd):
    print(">>>", " ".join(cmd))
    subprocess.check_call(cmd)

if __name__ == "__main__":
    run([sys.executable, "scripts/run_canonical_runs.py"])
    run([sys.executable, "scripts/run_regulator_scan.py"])
    run([sys.executable, "scripts/fit_sensitivities.py"])
    run([sys.executable, "scripts/run_variant_comparison.py"])
    run([sys.executable, "scripts/run_sensitivity_convergence.py"])
    run([sys.executable, "scripts/cconv_rescaling_example.py"])
    run([sys.executable, "scripts/run_mu_sensitivity.py"])
    run([sys.executable, "scripts/run_richardson_and_residuals.py"])
    print("\nALL DONE. See outputs/.")
