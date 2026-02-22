#!/usr/bin/env python3
"""Build Maintext observables table from runs_summary.csv.

Produces: outputs/tables/maintext_observables_table.csv
Inputs: outputs/runs_summary.csv

This script intentionally uses only artifacts committed in-repo.
"""
from __future__ import annotations
import argparse
import pandas as pd

G = 6.67430e-11
c = 299792458.0
Msun = 1.98847e30

def k2_from_lambda_R(Lambda14: float, R14_km: float, M14_Msun: float = 1.4) -> float:
    R = R14_km * 1000.0
    M = M14_Msun * Msun
    C = G * M / (R * c**2)
    return 1.5 * Lambda14 * (C**5)

def fmt_range(lo: float, hi: float, fmt: str) -> str:
    return f"{fmt.format(lo)}–{fmt.format(hi)}"


def overlap_iou(a: tuple[float,float], b: tuple[float,float]) -> float:
    """Intersection-over-union proxy for overlap of two 1D 90% CI intervals."""
    (x1,x2),(y1,y2)=a,b
    inter=max(0.0, min(x2,y2)-max(x1,y1))
    union=max(x2,y2)-min(x1,y1)
    return inter/union if union>0 else 0.0

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--runs', default='outputs/runs_summary.csv')
    ap.add_argument('--eos', default='SLy-PP(Read2009),AP4-PP(Read2009),MPA1-PP(Read2009)')
    ap.add_argument('--out', default='outputs/tables/maintext_observables_table.csv')
    args = ap.parse_args()

    eos_list = [e.strip() for e in args.eos.split(',') if e.strip()]
    df = pd.read_csv(args.runs)

    def select(case: str):
        return df[(df['EOS'].isin(eos_list)) & (df['case'] == case) & (df['obs_status'] == 'accepted')]

    sm = select('A_baseline')
    sfst = select('C_sigma_chi')

    if sm.empty or sfst.empty:
        raise SystemExit('No accepted runs found for requested EOS/cases.')

    # Ranges across EOS-set (simple sanity table)
    R_sm = (sm['R_1.4'].min(), sm['R_1.4'].max())
    R_sfst = (sfst['R_1.4'].min(), sfst['R_1.4'].max())

    L_sm = (sm['Lambda_1.4'].min(), sm['Lambda_1.4'].max())
    L_sfst = (sfst['Lambda_1.4'].min(), sfst['Lambda_1.4'].max())

    M_sm = (sm['Mmax'].min(), sm['Mmax'].max())
    M_sfst = (sfst['Mmax'].min(), sfst['Mmax'].max())

    k2_sm_vals = [k2_from_lambda_R(L,R) for L,R in zip(sm['Lambda_1.4'], sm['R_1.4'])]
    k2_sfst_vals = [k2_from_lambda_R(L,R) for L,R in zip(sfst['Lambda_1.4'], sfst['R_1.4'])]
    k2_sm = (min(k2_sm_vals), max(k2_sm_vals))
    k2_sfst = (min(k2_sfst_vals), max(k2_sfst_vals))

    # EOS-wise deltaR
    dR = (sfst.set_index('EOS')['R_1.4'] - sm.set_index('EOS')['R_1.4']).dropna()
    dR_rng = (float(dR.min()), float(dR.max()))

    out = pd.DataFrame([
        {'Observable':'R1.4 [km]', 'Standard model (range)': fmt_range(*R_sm, fmt='{:.2f}'), 'SFST (range)': fmt_range(*R_sfst, fmt='{:.2f}')},
        {'Observable':'Λ1.4 [–]', 'Standard model (range)': f"{L_sm[0]:.0f}–{L_sm[1]:.0f}", 'SFST (range)': f"{L_sfst[0]:.0f}–{L_sfst[1]:.0f}"},
        {'Observable':'Mmax [M⊙]', 'Standard model (range)': fmt_range(*M_sm, fmt='{:.2f}'), 'SFST (range)': fmt_range(*M_sfst, fmt='{:.2f}')},
        {'Observable':'k2,1.4 [–]', 'Standard model (range)': fmt_range(*k2_sm, fmt='{:.3f}'), 'SFST (range)': fmt_range(*k2_sfst, fmt='{:.3f}')},
        {'Observable':'ΔR1.4 [km]', 'Standard model (range)': '0 (reference)', 'SFST (range)': fmt_range(*dR_rng, fmt='{:+.2f}')},
        {
            'Observable':'Posterior overlap (proxy)',
            'Standard model (range)':'',
            'SFST (range)': (
                'IoU(90% CI proxy): '
                + f"R1.4={overlap_iou(R_sm,R_sfst):.2f}, "
                + f"Λ1.4={overlap_iou(L_sm,L_sfst):.2f}, "
                + f"Mmax={overlap_iou(M_sm,M_sfst):.2f}, "
                + f"k2={overlap_iou(k2_sm,k2_sfst):.2f}"
            )
        },
    ])
    out.to_csv(args.out, index=False)
    print(f"Wrote {args.out}")

if __name__ == '__main__':
    main()
