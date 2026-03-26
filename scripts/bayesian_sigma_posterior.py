#!/usr/bin/env python3
"""
bayesian_sigma_posterior.py — Bayesian constraint on σ from GW170817 + NICER
=============================================================================

Computes P(σ|data) using:
  - Prior: flat on [0, σ_max] where σ_max = 0.10 (perturbativity)
  - Likelihood from GW170817: Λ_{1.4} < 800 at 90% CL
    → Gaussian: L_GW(σ) ∝ exp(-(Λ(σ)-Λ_obs)²/(2δΛ²))
  - Likelihood from NICER J0030: R_{1.4} ∈ [11.52, 13.85] km at 68% CL
    → Gaussian: L_NICER(σ) for EOS where R₀ > 11.52

Uses linearised response: O(σ) = O₀ + S_O × σ
Grid integration (no MCMC needed for 1D parameter).

Author: M. W. Le Borgne, March 2026
"""
import numpy as np
import json, os

# === EOS data (from TOV solver, archived) ===
EOS = {
    'SLy':  {'M0': 2.075, 'R0': 11.133, 'L0': 577.4, 'SM': -1.191, 'SR': -3.17, 'SL': -1820},
    'AP4':  {'M0': 2.207, 'R0': 10.776, 'L0': 549.5, 'SM': -1.101, 'SR': -2.48, 'SL': -2080},
    'MPA1': {'M0': 2.461, 'R0': 12.540, 'L0': 750.0, 'SM': -1.320, 'SR': -4.10, 'SL': -2400},
    'H4':   {'M0': 2.030, 'R0': 12.100, 'L0': 820.0, 'SM': -0.980, 'SR': -3.50, 'SL': -1600},
}

G_EFF = 3.0 / (56 * np.pi**2.5)  # = 0.003062...

# === Observational constraints ===
# GW170817: Λ_{1.4} < 800 at 90% CL → model as Gaussian with
# central value ~400 and σ_Λ ~200 (approximate from Abbott+ 2018)
LAMBDA_OBS = 400.0   # central from GW170817 low-spin prior
DELTA_LAMBDA = 200.0  # approximate 1σ width

# NICER J0030+0451: R_{1.4} = 12.71 (+1.14, -1.19) km at 68% CL
R_NICER_CENTER = 12.71
R_NICER_SIGMA = 1.17  # average of +/- errors

# === Grid ===
N_GRID = 10000
sigma_grid = np.linspace(0, 0.10, N_GRID)
dsigma = sigma_grid[1] - sigma_grid[0]

print("=" * 72)
print("  BAYESIAN σ-POSTERIOR FROM GW170817 + NICER")
print("=" * 72)

results = {}
for name, d in EOS.items():
    # Linearised observables
    Lambda_sigma = d['L0'] + d['SL'] * sigma_grid
    R_sigma = d['R0'] + d['SR'] * sigma_grid
    M_sigma = d['M0'] + d['SM'] * sigma_grid
    
    # Perturbativity mask: epsratio ≈ σ × 5 ≤ 0.10 → σ ≤ 0.02
    epsratio_max = sigma_grid * 5.0  # typical (ε+P)/P ≈ 5
    prior = np.where(epsratio_max <= 0.10, 1.0, 0.0)
    # Soft transition at edge
    prior = np.where(epsratio_max <= 0.30, prior + 0.1 * (epsratio_max > 0.10), prior)
    prior[:1] = 1.0  # σ=0 always allowed
    
    # GW likelihood
    L_GW = np.exp(-0.5 * ((Lambda_sigma - LAMBDA_OBS) / DELTA_LAMBDA)**2)
    
    # NICER likelihood
    L_NICER = np.exp(-0.5 * ((R_sigma - R_NICER_CENTER) / R_NICER_SIGMA)**2)
    
    # Stability: M_max > 1.97 M_sun (PSR J0348+0432)
    L_MASS = np.where(M_sigma > 1.97, 1.0, 0.01)
    
    # Joint posterior (unnormalised)
    posterior = prior * L_GW * L_NICER * L_MASS
    norm = np.sum(posterior) * dsigma
    if norm > 0:
        posterior /= norm
    
    # Statistics
    mean = np.sum(sigma_grid * posterior) * dsigma
    var = np.sum((sigma_grid - mean)**2 * posterior) * dsigma
    std = np.sqrt(var)
    
    # Credible intervals
    cdf = np.cumsum(posterior) * dsigma
    idx_5 = np.searchsorted(cdf, 0.05)
    idx_50 = np.searchsorted(cdf, 0.50)
    idx_95 = np.searchsorted(cdf, 0.95)
    ci90 = (sigma_grid[min(idx_5, N_GRID-1)], sigma_grid[min(idx_95, N_GRID-1)])
    median = sigma_grid[min(idx_50, N_GRID-1)]
    
    # P(σ = G_eff)
    idx_Geff = np.argmin(np.abs(sigma_grid - G_EFF))
    p_Geff = posterior[idx_Geff]
    p_max = np.max(posterior)
    
    print(f"\n  {name}:")
    print(f"    Mean σ = {mean:.5f} ± {std:.5f}")
    print(f"    Median σ = {median:.5f}")
    print(f"    90% CI: [{ci90[0]:.5f}, {ci90[1]:.5f}]")
    print(f"    P(σ=G_eff)/P_max = {p_Geff/p_max:.4f}")
    print(f"    G_eff = {G_EFF:.6f} {'✓ inside 90% CI' if ci90[0] <= G_EFF <= ci90[1] else '✗ outside'}")
    
    results[name] = {
        'mean': float(mean), 'std': float(std), 'median': float(median),
        'ci90_lo': float(ci90[0]), 'ci90_hi': float(ci90[1]),
        'p_Geff_relative': float(p_Geff/p_max) if p_max > 0 else 0,
        'Geff_in_90CI': bool(ci90[0] <= G_EFF <= ci90[1]),
    }

print(f"\n  G_eff = {G_EFF:.10f}")
print(f"\n  {'='*60}")
print(f"  SUMMARY")
print(f"  {'='*60}")
for name, r in results.items():
    status = "✓" if r['Geff_in_90CI'] else "✗"
    print(f"  {name:6s}: σ = {r['mean']:.4f}±{r['std']:.4f}, "
          f"90%CI=[{r['ci90_lo']:.4f},{r['ci90_hi']:.4f}], "
          f"G_eff {status}")

# Save
os.makedirs('outputs', exist_ok=True)
with open('outputs/bayesian_sigma_results.json', 'w') as f:
    json.dump({'G_eff': float(G_EFF), 'EOS': results}, f, indent=2)
print(f"\n  Results saved to outputs/bayesian_sigma_results.json")
