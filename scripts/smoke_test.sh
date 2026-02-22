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

# Expected columns (match sfst_qfis_repro.run_canonical output)
required = ["EOS","Mmax","R_1.4","Lambda_1.4"]
missing = [c for c in required if c not in df.columns]
if missing:
    print("Missing columns:", missing)
    print("Available columns:", list(df.columns))
    sys.exit(2)

row = df[df["EOS"].astype(str).str.contains("SLy", case=False, na=False)]
if len(row)==0:
    print("No SLy row found in", path)
    sys.exit(2)

# Prefer Variant A baseline row if present (case label may vary)
# Fall back to first SLy row.
r = row.sort_values(by=[c for c in ["case","inc_g"] if c in row.columns]).iloc[0]
Mmax = float(r["Mmax"])
R14 = float(r["R_1.4"])
Lam = float(r["Lambda_1.4"])

def in_range(x,a,b): return (x>=a) and (x<=b)
ok = True

# Loose sanity ranges (do not over-constrain CI)
if not in_range(Mmax, 1.8, 2.4):
    print(f"FAIL: Mmax_SLy={Mmax} not in [1.8,2.4]")
    ok=False
if not in_range(R14, 8.0, 14.0):
    print(f"FAIL: R_1.4_SLy_km={R14} not in [8.0,14.0]")
    ok=False
if not (math.isfinite(Lam) and Lam>0):
    print(f"FAIL: Lambda_1.4_SLy={Lam} not finite/positive")
    ok=False

if not ok:
    sys.exit(1)

print("PASS: smoke test checks succeeded.")
PY
