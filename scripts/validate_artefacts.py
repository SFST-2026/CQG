#!/usr/bin/env python3
import sys, pandas as pd, pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"
fails = 0

def check_no_nan(path):
    global fails
    df = pd.read_csv(path)
    if df.isna().any().any():
        n = int(df.isna().sum().sum())
        print(f"[FAIL] NaNs found in {path} ({n} cells)")
        fails += 1
    else:
        print(f"[OK] no NaNs: {path}")

def check_poly2_not_identical():
    p = OUT / "summary_canonical_runs.csv"
    df = pd.read_csv(p)
    poly = df[df["EOS"].str.contains("Poly2", na=False)]
    if len(poly) >= 2:
        r_unique = poly["R_1.4_km"].round(6).nunique()
        l_unique = poly["Lambda_1.4"].round(3).nunique()
        if r_unique == 1 and l_unique == 1:
            print("[WARN] Poly2 rows have identical R_1.4 and Lambda_1.4. If intended, document as toy-EOS artefact.")
        else:
            print("[OK] Poly2 rows vary across cases.")
    else:
        print("[INFO] No Poly2 entries in summary (ok).")

check_no_nan(OUT / "summary_canonical_runs.csv")
check_poly2_not_identical()

if fails:
    sys.exit(1)
print("[OK] artefact validation passed.")
