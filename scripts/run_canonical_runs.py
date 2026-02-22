import os
import sys

# Ensure repo root is importable when this script is executed as a file.
_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from pathlib import Path
import pandas as pd
from sfst_qfis_repro import run_canonical

if __name__ == "__main__":
    outdir = Path("outputs")
    outdir.mkdir(exist_ok=True)
    df = run_canonical(outdir=str(outdir), sigma_legacy=0.04, chi_legacy=1.0, sigma_vac=0.06, chi_vac=1.0, screening_factor=1.0, include_in_gravity=False)
    print(df)
    print("\nWrote outputs/summary_canonical_runs.csv and per-EOS CSV/plots.")
