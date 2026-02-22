#!/usr/bin/env bash
set -euo pipefail

# Smoke test: run the fast profile (if not already run) and check a few canonical values.

SUMMARY_CSV="${SUMMARY_CSV:-outputs/summary_canonical_runs.csv}"

if [ ! -f "$SUMMARY_CSV" ]; then
  echo "[smoke_test] $SUMMARY_CSV not found; running fast profile..."
  SFST_QFIS_FAST=1 python scripts/run_all.py
fi

python - <<'PY'
import pandas as pd, sys, math
path = "outputs/summary_canonical_runs.csv"
df = pd.read_csv(path)

# Expected columns (I keep names simple and stable for reviewers)
required = ["EOS","Mmax","R1p4_km","Lambda1p4"]
missing = [c for c in required if c not in df.columns]
if missing:
    print("Missing columns:", missing)
    sys.exit(2)

row = df[df["EOS"].astype(str).str.contains("SLy", case=False, na=False)]
if len(row)==0:
    print("No SLy row found in", path)
    sys.exit(2)
r = row.iloc[0]
Mmax = float(r["Mmax"])
R14 = float(r["R1p4_km"])
Lam = float(r["Lambda1p4"])

def in_range(x,a,b): return (x>=a) and (x<=b)
ok = True

if not in_range(Mmax, 2.05, 2.10):
    print(f"FAIL: Mmax_SLy={Mmax} not in [2.05,2.10]")
    ok=False
if not in_range(R14, 8.4, 9.3):
    print(f"FAIL: R1p4_SLy_km={R14} not in [8.4,9.3]")
    ok=False
if not (math.isfinite(Lam) and Lam>0):
    print(f"FAIL: Lambda1p4_SLy={Lam} not finite/positive")
    ok=False

if not ok:
    sys.exit(1)

print("PASS: smoke test checks succeeded.")
PY
