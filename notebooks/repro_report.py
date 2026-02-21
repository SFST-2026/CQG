# This is a notebook-style script that compiles plots/tables for the manuscript.
# Run: python notebooks/repro_report.py
from pathlib import Path
import pandas as pd

out = Path("outputs")
summary = pd.read_csv(out/"summary_canonical_runs.csv")
sens = pd.read_csv(out/"sensitivities_from_canonical.csv")
print("Summary:"); print(summary.head())
print("\nSensitivities:"); print(sens.head())
print("\nSee outputs/ for figures produced by the scripts.")
