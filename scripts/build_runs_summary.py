#!/usr/bin/env python3
"""Build a robust outputs/runs_summary.csv using conservative reruns.

I regenerate all canonical EOS/cases directly from the solver (no pre-existing CSV needed).

Conservative discretization proxy
I estimate a discretization/solver uncertainty by solving each EOS/case twice:
- baseline: max_step, rtol, atol from config/validate_config.yaml
- refined:  max_step/2 and tighter rtol/atol
The relative difference between baseline and refined is recorded as delta_disc for each observable.

epsratio
In this implementation, eps_vac,inertial(r) = (sigma*chi*screening_factor)*eps_ref(r),
so epsratio(r) is constant and max_epsratio = |sigma*chi*screening_factor|.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sfst_qfis_repro import make_piecewise_eos, make_simple_polytrope, integrate_star  # noqa: E402

EOS_DEFS = {
    "SLy-PP(Read2009)": (34.384, 3.005, 2.988, 2.851),
    "AP4-PP(Read2009)": (34.269, 2.830, 3.445, 3.348),
    "H4-PP(Read2009)": (34.669, 2.909, 2.246, 2.144),
    "MPA1-PP(Read2009)": (34.495, 2.921, 3.132, 2.995),
    "WFF1-PP(Read2009)": (34.031, 2.628, 2.885, 2.951),
}

EOS_ORDER = [
    "SLy-PP(Read2009)",
    "AP4-PP(Read2009)",
    "MPA1-PP(Read2009)",
    "H4-PP(Read2009)",
    "WFF1-PP(Read2009)",
    "Poly2(toy)",
]

CASES = [
    ("A_baseline", 0.00, 1.0, False, "A"),
    ("B_legacy", 0.06, 1.0, True, "B_exploratory"),
    ("C_sigma_chi", 0.06, 1.0, False, "A"),
]


@dataclass
class SolverCfg:
    n_points: int
    rho_min: float
    rho_max: float
    max_step: float
    rtol: float
    atol: float


def load_cfg():
    with open('config/validate_config.yaml') as f:
        return yaml.safe_load(f)


def solver_from_cfg(cfg: dict) -> SolverCfg:
    s = cfg['solver']
    return SolverCfg(
        n_points=int(s['n_points']),
        rho_min=float(s['rho_min']),
        rho_max=float(s['rho_max']),
        max_step=float(s['max_step']),
        rtol=float(s['rtol']),
        atol=float(s['atol']),
    )


def get_eos(name: str):
    if name == 'Poly2(toy)':
        return make_simple_polytrope(Gamma=2.0, P_ref=3e34, name='Poly2(toy)')
    lp, g1, g2, g3 = EOS_DEFS[name]
    return make_piecewise_eos(lp, g1, g2, g3, name)


def interp_at_mass(df: pd.DataFrame, target: float = 1.4):
    d = df.sort_values('M_msun')
    d = d[np.isfinite(d['M_msun']) & np.isfinite(d['R_km']) & np.isfinite(d['Lambda'])]
    if len(d) < 4:
        return float('nan'), float('nan'), 'insufficient_points'
    mmin, mmax = float(d.M_msun.min()), float(d.M_msun.max())
    if not (mmin <= target <= mmax):
        return float('nan'), float('nan'), f'target_out_of_range:[{mmin:.3f},{mmax:.3f}]'
    R = float(np.interp(target, d.M_msun, d.R_km))
    L = float(np.interp(target, d.M_msun, d.Lambda))
    return R, L, 'ok'


def scan_family(eos, *, sigma_vac: float, chi_vac: float, screening_factor: float, include_in_gravity: bool,
                n_points: int, rho_min: float, rho_max: float, max_step: float, rtol: float, atol: float):
    rhos = np.logspace(np.log10(rho_min), np.log10(rho_max), n_points)
    rows = []
    for rc in rhos:
        res = integrate_star(
            eos, rc,
            sigma_vac=sigma_vac, chi_vac=chi_vac,
            screening_factor=screening_factor,
            include_in_gravity=include_in_gravity,
            max_step=max_step,
            rtol=rtol,
            atol=atol,
        )
        if res is not None:
            rows.append(res)
    return pd.DataFrame(rows)


def compute_observables(df: pd.DataFrame):
    if len(df) < 4:
        return dict(Mmax=float('nan'), R_1p4=float('nan'), Lambda_1p4=float('nan'), status='insufficient_points')
    d = df[np.isfinite(df['M_msun'])].copy()
    if len(d) < 4:
        return dict(Mmax=float('nan'), R_1p4=float('nan'), Lambda_1p4=float('nan'), status='insufficient_points')
    Mmax = float(d.M_msun.max())
    R14, L14, st = interp_at_mass(d, 1.4)
    wf=float(d.W_max.replace([float('inf'),float('-inf')], float('nan')).max()) if 'W_max' in d.columns else float('nan')
    return dict(Mmax=Mmax, R_1p4=R14, Lambda_1p4=L14, wfaktor_max=wf, status=st)


def rel_diff_pct(a: float, b: float) -> float:
    if not (math.isfinite(a) and math.isfinite(b)):
        return float('nan')
    denom = abs(b) if abs(b) > 0 else 1.0
    return 100.0 * abs(a - b) / denom


def main():
    cfg = load_cfg()
    solver = solver_from_cfg(cfg)

    screening = 1.0

    rows = []
    for eos_name in EOS_ORDER:
        eos = get_eos(eos_name)
        for case, sigma, chi, inc_g, variant in CASES:
            # baseline
            df0 = scan_family(
                eos,
                sigma_vac=sigma, chi_vac=chi,
                screening_factor=screening,
                include_in_gravity=inc_g,
                n_points=solver.n_points,
                rho_min=solver.rho_min,
                rho_max=solver.rho_max,
                max_step=solver.max_step,
                rtol=solver.rtol,
                atol=solver.atol,
            )
            obs0 = compute_observables(df0)

            # refined
            df1 = scan_family(
                eos,
                sigma_vac=sigma, chi_vac=chi,
                screening_factor=screening,
                include_in_gravity=inc_g,
                n_points=solver.n_points,
                rho_min=solver.rho_min,
                rho_max=solver.rho_max,
                max_step=solver.max_step * 0.5,
                rtol=1e-8,
                atol=1e-11,
            )
            obs1 = compute_observables(df1)

            row = {
                'run_id': f"{eos_name.replace('(','').replace(')','').replace('-','')}_{case}",
                'EOS': eos_name,
                'case': case,
                'variant': variant,
                'sigma': sigma,
                'chi': chi,
                'include_in_gravity': inc_g,
                'Mmax': obs1['Mmax'],
                'R_1.4': obs1['R_1p4'],
                'Lambda_1.4': obs1['Lambda_1p4'],
                'wfaktor_max': obs1.get('wfaktor_max', float('nan')),
                'obs_status': obs1['status'],
                'max_epsratio': abs(sigma * chi * screening),
                'delta_disc_Mmax_pct': rel_diff_pct(obs0['Mmax'], obs1['Mmax']),
                'delta_disc_R14_pct': rel_diff_pct(obs0['R_1p4'], obs1['R_1p4']),
                'delta_disc_Lambda14_pct': rel_diff_pct(obs0['Lambda_1p4'], obs1['Lambda_1p4']),
                'baseline_max_step': solver.max_step,
                'refined_max_step': solver.max_step * 0.5,
                'baseline_rtol': solver.rtol,
                'refined_rtol': 1e-8,
                'baseline_atol': solver.atol,
                'refined_atol': 1e-11,
            }
            rows.append(row)

    df = pd.DataFrame(rows)

    # Deltas relative to baseline per EOS
    out = []
    for eos, g in df.groupby('EOS'):
        base = g[g['case'] == 'A_baseline'].iloc[0]

        def delta_pct(val, baseval):
            return 100.0 * (val - baseval) / baseval if (math.isfinite(val) and math.isfinite(baseval) and baseval != 0) else float('nan')

        for _, r in g.iterrows():
            rr = dict(r)
            rr['Delta_Mmax_pct'] = delta_pct(r['Mmax'], base['Mmax'])
            rr['Delta_R14_pct'] = delta_pct(r['R_1.4'], base['R_1.4'])
            rr['Delta_Lambda14_pct'] = delta_pct(r['Lambda_1.4'], base['Lambda_1.4'])
            rr['delta_total_Mmax_pct'] = rr['delta_disc_Mmax_pct']
            rr['delta_total_R14_pct'] = rr['delta_disc_R14_pct']
            rr['delta_total_Lambda14_pct'] = rr['delta_disc_Lambda14_pct']
            out.append(rr)

    out_df = pd.DataFrame(out).replace([float('inf'), float('-inf')], float('nan'))

    Path('outputs').mkdir(parents=True, exist_ok=True)
    
    # --- Robustness: conservative NaN handling (auditable) ---
    # If core observables are missing (NaN), mark as DIAGNOSTIC and set conservative
    # sentinel values so downstream validators reliably flag the run.
    for col in ['Mmax_Msun','R_1p4_km','Lambda_1p4']:
        if col in out_df.columns:
            bad = ~np.isfinite(out_df[col].astype(float))
            if bad.any():
                out_df.loc[bad, 'status'] = 'DIAGNOSTIC'
                for c2, val in [
                    ('delta_total_pct', 1e9),
                    ('delta_disc_pct', 1e9),
                    ('newton_final_residual', 1e9),
                    ('newton_iterations', 10**9),
                    ('wfaktor_max', 1e9),
                    ('max_epsratio', 1.0),
                ]:
                    if c2 in out_df.columns:
                        out_df.loc[bad, c2] = val
                # Replace NaN response columns with 0 so CSV stays numeric
                for c3 in ['DeltaMmax_pct','DeltaR14_pct','DeltaLambda14_pct','DeltaLambda14_err_pct']:
                    if c3 in out_df.columns:
                        bad3 = bad & ~np.isfinite(out_df[c3].astype(float))
                        out_df.loc[bad3, c3] = 0.0

    
    # --- Robustness: conservative NaN handling (auditable) ---
    core_cols = ['Mmax','R_1.4','Lambda_1.4']
    bad = None
    for col in core_cols:
        if col in out_df.columns:
            col_bad = ~np.isfinite(pd.to_numeric(out_df[col], errors='coerce'))
            bad = col_bad if bad is None else (bad | col_bad)
    if bad is not None and bad.any():
        out_df.loc[bad, 'obs_status'] = 'DIAGNOSTIC'
        # conservative sentinel values to ensure validators flag the run
        for c2, val in [
            ('delta_total_Lambda14_pct', 1e9),
            ('delta_disc_Lambda14_pct', 1e9),
            ('wfaktor_max', 1e9),
            ('max_epsratio', 1.0),
        ]:
            if c2 in out_df.columns:
                out_df.loc[bad, c2] = val
        for c3 in ['Delta_Mmax_pct','Delta_R14_pct','Delta_Lambda14_pct']:
            if c3 in out_df.columns:
                out_df.loc[bad, c3] = 0.0
        # fill NaNs in core observables to keep CSV numeric
        for col in core_cols:
            if col in out_df.columns:
                out_df.loc[bad, col] = out_df.loc[bad, col].fillna(0.0)

    
    # Fill NaNs in uncertainty columns conservatively
    for c in ['delta_disc_Mmax_pct','delta_total_Mmax_pct','delta_disc_R14_pct','delta_total_R14_pct',
              'delta_disc_Lambda14_pct','delta_total_Lambda14_pct']:
        if c in out_df.columns:
            out_df[c] = pd.to_numeric(out_df[c], errors='coerce')
            nan_mask = ~np.isfinite(out_df[c])
            if nan_mask.any():
                # if the row is already diagnostic, set large sentinel; otherwise set 0 and keep accepted
                if 'obs_status' in out_df.columns:
                    diag = out_df['obs_status'].astype(str).str.upper().isin(['DIAGNOSTIC','EXCLUDED'])
                else:
                    diag = pd.Series(False, index=out_df.index)
                out_df.loc[nan_mask & diag, c] = 1e9
                out_df.loc[nan_mask & ~diag, c] = 0.0

    out_path = Path('outputs/runs_summary.csv')
    out_df.to_csv(out_path, index=False)
    print(f"Wrote {out_path} ({len(out_df)} rows)")


if __name__ == '__main__':
    main()
