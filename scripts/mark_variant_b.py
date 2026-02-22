#!/usr/bin/env python3
"""Mark Variant-B runs as exploratory.

This script enforces the naming/visibility requirement:
- Any run with case containing 'B_' is marked as variant='B_exploratory'
- Otherwise defaults to variant='A' (unless already set)

It updates outputs/runs_summary.csv in-place.

Usage:
  python scripts/mark_variant_b.py
"""
from __future__ import annotations
import pandas as pd
from pathlib import Path

RUNS = Path('outputs/runs_summary.csv')

def main():
    df = pd.read_csv(RUNS)
    if 'variant' not in df.columns:
        df['variant'] = 'A'
    mask_b = df['case'].astype(str).str.contains('^B_', regex=True, na=False) | df['case'].astype(str).str.contains('B_legacy', na=False)
    df.loc[mask_b, 'variant'] = 'B_exploratory'
    df.loc[~mask_b & (df['variant'].isna() | (df['variant'].astype(str).str.strip() == '')), 'variant'] = 'A'
    df.to_csv(RUNS, index=False)
    print(f'Updated {RUNS} (B_exploratory rows: {int(mask_b.sum())})')

if __name__ == '__main__':
    main()
