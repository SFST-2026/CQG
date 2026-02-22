#!/usr/bin/env python3
"""Create paired ΔΛ_1.4 envelopes: excluding vs including diagnostics.

Solid band: accepted + stress only.
Dashed band: all runs (including diagnostic/excluded).

Output: figures/lambda1p4_paired_including_excluding.png
"""

from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def envelope(df: pd.DataFrame, eos_order: list[str]) -> pd.DataFrame:
    out = []
    for eos in eos_order:
        g = df[df['EOS'] == eos]
        if len(g) == 0:
            out.append((eos, np.nan, np.nan, np.nan, 0))
            continue
        vals = g['Delta_Lambda14_pct'].astype(float).values
        errs = g['delta_total_Lambda14_pct'].astype(float).values
        errs = np.where(np.isfinite(errs), errs, 0.0)
        samp = []
        for d, e in zip(vals, errs):
            if not np.isfinite(d):
                continue
            if e <= 0:
                samp.append(np.full(200, d))
            else:
                samp.append(np.random.normal(d, e, size=400))
        if samp:
            samp = np.concatenate(samp)
            lo, med, hi = np.percentile(samp, [5, 50, 95])
        else:
            lo = med = hi = np.nan
        out.append((eos, med, lo, hi, len(g)))
    return pd.DataFrame(out, columns=['EOS', 'median', 'p5', 'p95', 'n'])


def main():
    rs_path = Path('outputs/runs_summary.csv')
    ai_path = Path('outputs/audit_index.csv')
    if not rs_path.exists() or not ai_path.exists():
        raise SystemExit('Run scripts/build_runs_summary.py and scripts/validate_run.py first.')

    all_df = pd.read_csv(rs_path)
    audit = pd.read_csv(ai_path)[['run_id','status']]
    all_df = all_df.merge(audit, on='run_id', how='left')

    all_df = all_df[all_df['case'] != 'A_baseline'].copy()

    eos_order = list(pd.unique(all_df['EOS']))

    incl = all_df.copy()
    excl = all_df[all_df['status'].isin(['accepted', 'stress'])].copy()

    env_incl = envelope(incl, eos_order)
    env_excl = envelope(excl, eos_order)

    x = np.arange(len(eos_order))

    plt.figure(figsize=(10, 4.8))

    plt.plot(x, env_excl['median'].values, linestyle='-')
    plt.fill_between(x, env_excl['p5'].values, env_excl['p95'].values, alpha=0.22)

    plt.plot(x, env_incl['median'].values, linestyle='--')
    plt.fill_between(x, env_incl['p5'].values, env_incl['p95'].values, alpha=0.12)

    plt.xticks(x, eos_order, rotation=30, ha='right')
    plt.ylabel('ΔΛ_1.4 [%]')
    plt.title('Paired ΔΛ_1.4 envelopes: excluding vs including diagnostics')

    for xi, n_ex, n_in in zip(x, env_excl['n'].values, env_incl['n'].values):
        plt.text(xi, 0.0, f"{int(n_ex)}/{int(n_in)}", ha='center', va='bottom', fontsize=8)

    Path('figures').mkdir(parents=True, exist_ok=True)
    out_path = Path('figures/lambda1p4_paired_including_excluding.png')
    plt.tight_layout()
    plt.savefig(out_path, dpi=200)
    print(f"Wrote {out_path}")


if __name__ == '__main__':
    main()
