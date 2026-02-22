"""
TOV + tidal Love solver (reference)

Units:
- EOS is defined in cgs internally.
- TOV equations integrated in geometrized G=c=1 with length in cm.
"""
from __future__ import annotations
import numpy as np
import os
FAST_CI = os.getenv('SFST_QFIS_FAST', '0') == '1'

import pandas as pd
from dataclasses import dataclass
from scipy.integrate import solve_ivp

# Constants
G_cgs = 6.67430e-8
c_cgs = 2.99792458e10
Msun_cgs = 1.98847e33
Msun_geom_cm = G_cgs * Msun_cgs / c_cgs**2
P_to_geom = G_cgs / c_cgs**4  # dyne/cm^2 -> geom

rho1 = 10**14.7
rho2 = 10**15.0

@dataclass(frozen=True)
class EOS:
    name: str
    params: dict
    P_of_rho: callable
    rho_eps_depsdP_of_P: callable


def make_polytrope_eos(K: float, Gamma: float, name: str) -> EOS:
    """Simple single-polytrope EOS (toy / diagnostic).
    P = K * rho^Gamma (cgs). Energy density eps ≈ rho*c^2 + P/(Gamma-1).
    """
    c2 = c_cgs**2
    def P_of_rho(rho_cgs: float):
        P = K * (rho_cgs**Gamma)
        eps = rho_cgs*c2 + P/(Gamma-1.0)
        return float(P), float(eps)

    def rho_eps_depsdP_of_P(P_cgs: float):
        # Invert polytrope: rho = (P/K)^(1/Gamma)
        rho = (max(P_cgs,0.0)/K)**(1.0/Gamma) if P_cgs>0 else 0.0
        eps = rho*c2 + P_cgs/(Gamma-1.0)
        # d eps / d P at fixed rho? Here derivative of eps(P) via rho(P):
        # eps(P)=rho(P)c^2 + P/(Gamma-1), rho(P)=(P/K)^(1/Gamma)
        if P_cgs<=0:
            depsdP = 1.0/(Gamma-1.0)
        else:
            drhodP = (1.0/Gamma)*(1.0/K)**(1.0/Gamma)*(P_cgs**(1.0/Gamma - 1.0))
            depsdP = drhodP*c2 + 1.0/(Gamma-1.0)
        return float(rho), float(eps), float(depsdP)

    return EOS(name=name, params={"K":K,"Gamma":Gamma}, P_of_rho=P_of_rho, rho_eps_depsdP_of_P=rho_eps_depsdP_of_P)

def make_piecewise_eos(log10p1: float, g1: float, g2: float, g3: float, name: str) -> EOS:
    p1 = 10**log10p1
    K1 = p1 / (rho1**g1)
    K2 = K1 * rho1**(g1-g2)
    K3 = K2 * rho2**(g2-g3)
    P1 = K1*rho1**g1
    P2 = K2*rho2**g2

    alpha1 = 0.0
    def eps_from_rhoP(rho, P, Gamma, alpha):
        return (1+alpha)*rho*c_cgs**2 + P/(Gamma-1)

    eps1 = eps_from_rhoP(rho1, P1, g1, alpha1)
    alpha2 = eps1/(rho1*c_cgs**2) - 1 - P1/((g2-1)*rho1*c_cgs**2)
    eps2 = eps_from_rhoP(rho2, P2, g2, alpha2)
    alpha3 = eps2/(rho2*c_cgs**2) - 1 - P2/((g3-1)*rho2*c_cgs**2)

    def segment_for_P(P):
        if P < P1:
            return K1, g1, alpha1
        elif P < P2:
            return K2, g2, alpha2
        else:
            return K3, g3, alpha3

    def P_of_rho(rho):
        if rho < rho1:
            K,Gm,a = K1,g1,alpha1
        elif rho < rho2:
            K,Gm,a = K2,g2,alpha2
        else:
            K,Gm,a = K3,g3,alpha3
        P = K*rho**Gm
        eps = eps_from_rhoP(rho, P, Gm, a)
        return P, eps

    def rho_eps_depsdP_of_P(P):
        K,Gm,a = segment_for_P(P)
        rho = (P/K)**(1/Gm)
        eps = eps_from_rhoP(rho, P, Gm, a)
        drho_dP = rho/(Gm*P)
        deps_dP = (1+a)*c_cgs**2*drho_dP + 1/(Gm-1)
        return rho, eps, deps_dP

    return EOS(name=name, params={"log10p1": log10p1, "Gamma1": g1, "Gamma2": g2, "Gamma3": g3},
               P_of_rho=P_of_rho, rho_eps_depsdP_of_P=rho_eps_depsdP_of_P)

def make_simple_polytrope(Gamma=2.0, rho_ref=1e14, P_ref=1e34, name="Poly2") -> EOS:
    K = P_ref/(rho_ref**Gamma)
    alpha=0.0
    def P_of_rho(rho):
        P = K*rho**Gamma
        eps = (1+alpha)*rho*c_cgs**2 + P/(Gamma-1)
        return P, eps
    def rho_eps_depsdP_of_P(P):
        rho = (P/K)**(1/Gamma)
        eps = (1+alpha)*rho*c_cgs**2 + P/(Gamma-1)
        drho_dP = rho/(Gamma*P)
        deps_dP = (1+alpha)*c_cgs**2*drho_dP + 1/(Gamma-1)
        return rho, eps, deps_dP
    return EOS(name=name, params={"Gamma": Gamma, "K": K}, P_of_rho=P_of_rho, rho_eps_depsdP_of_P=rho_eps_depsdP_of_P)

def tov_rhs(r, y, eos: EOS, *, sigma_vac: float, chi_vac: float, screening_factor: float, include_in_gravity: bool):
    m, P, yt = y
    if P <= 0.0 or r <= 0.0:
        return [0.0, 0.0, 0.0]
    P_cgs = P / P_to_geom
    _, eps_cgs, deps_dP_cgs = eos.rho_eps_depsdP_of_P(P_cgs)

    # Base (gravitational-source) energy density from EOS
    eps_grav = (eps_cgs * P_to_geom)

    # --- Paper-conform insertion (Variant A by default): vacuum-induced inertia affects inertial response,
    #     not the gravitational source term unless include_in_gravity=True.
    #
    # I model m_vac(r) = sigma_vac * chi_vac * S(r) * V_cell.
    # In this 1D reference solver I work with densities; therefore I insert an *inertial energy-density*
    # increment eps_vac_inertial such that it contributes to the inertial factor (eps+P) but not to dm/dr
    # when include_in_gravity=False.
    #
    # NOTE: Without an explicit microphysical mapping for m_bare per cell in the manuscript, the reference
    # implementation treats (sigma_vac*chi_vac*S) as an effective local inertial energy-density increment.
    # Replace this mapping with your exact m_bare/V_cell prescription if available.

    # Simple screening model S(r): constant (default 1). Replace with your manuscript S(r) if specified.
    S = screening_factor

    delta_frac = sigma_vac * chi_vac * S  # dimensionless (paper: m_vac as additional inertial response)
    eps_vac_inertial = delta_frac * eps_grav  # inertial-only energy-density increment (fractional mapping)

    eps_inertial = eps_grav + eps_vac_inertial

    if include_in_gravity:
        eps_for_dm = eps_inertial
    else:
        eps_for_dm = eps_grav

    # For sound speed I use EOS derivative on the base EOS part (conservative).
    deps_dP = deps_dP_cgs
    cs2 = 1.0 / deps_dP

    C1 = 1.0 - 2.0*m/r
    dm = 4.0*np.pi*r**2 * eps_for_dm
    dP = -(eps_inertial+P) * (m + 4.0*np.pi*r**3 * P) / (r*(r-2.0*m))

    # Hinderer (l=2)
    eps_bg = eps_for_dm  # background energy density sourcing the metric
    F = (1.0 - 4.0*np.pi*r**2*(eps_bg - P)) / C1
    Q = (4.0*np.pi*(5.0*eps_bg + 9.0*P + (eps_bg+P)/cs2))/C1 - 6.0/(r**2) - 4.0*(m + 4.0*np.pi*r**3*P)**2/(r**4 * C1**2)
    dyt = -(yt**2)/r - (yt*F)/r - r*Q
    return [dm, dP, dyt]

def integrate_star(eos: EOS, rho_c_cgs: float, *, sigma_vac: float, chi_vac: float, screening_factor: float, include_in_gravity: bool, r0=1e-3, rmax=3e6, max_step=5e4, rtol=3e-6, atol=1e-9, store_profile: bool=False):
    P_c_cgs, eps_c_cgs = eos.P_of_rho(rho_c_cgs)
    P0 = P_c_cgs * P_to_geom
    eps0 = eps_c_cgs * P_to_geom * (1.0 + (sigma_vac*chi_vac*screening_factor/ (eps_c_cgs * P_to_geom)) if include_in_gravity else 1.0)
    m0 = 4.0/3.0*np.pi * r0**3 * eps0
    y0 = 2.0
    y_init = [m0, P0, y0]

    def surface(r,y): return y[1]
    surface.terminal=True
    surface.direction=-1

    sol = solve_ivp(lambda r,y: tov_rhs(r,y,eos, sigma_vac=sigma_vac, chi_vac=chi_vac, screening_factor=screening_factor, include_in_gravity=include_in_gravity), (r0, rmax), y_init,
                    events=surface, max_step=max_step, rtol=rtol, atol=atol)

    if len(sol.t_events[0]) == 0:
        return None

    R = float(sol.t_events[0][0])
    m = float(sol.y_events[0][0][0])
    yR = float(sol.y_events[0][0][2])
    C = m/R

    term1 = (8*C**5/5) * (1-2*C)**2 * (2 + 2*C*(yR-1) - yR)
    term2 = 2*C*(6 - 3*yR + 3*C*(5*yR-8))
    term2 += 4*C**3*(13 - 11*yR + C*(3*yR-2) + 2*C**2*(1+yR))
    term2 += 3*(1-2*C)**2*(2 - yR + 2*C*(yR-1))*np.log(1-2*C)
    k2 = term1/term2
    Lambda = (2.0/3.0)*k2/(C**5)

    if store_profile:
        # Build simple profiles for diagnostics (gravity-source energy density)
        r_prof = sol.t
        m_prof = sol.y[0]
        P_prof_geom = sol.y[1]
        # Convert P back to cgs to compute eps
        P_prof_cgs = P_prof_geom / P_to_geom
        eps_prof_cgs = np.array([eos.rho_eps_depsdP_of_P(float(P))[1] for P in P_prof_cgs])
        eps_prof_geom = eps_prof_cgs * P_to_geom
        # WFaktor diagnostic: dimensionless ratio of inertial vacuum energy density to (eps+P).
        eps_vac_geom = (sigma_vac*chi_vac*screening_factor) * P_to_geom
        W_prof = np.abs(eps_vac_geom) / (np.abs(eps_prof_geom + P_prof_geom) + 1e-99)
        W_max = float(np.nanmax(W_prof))
        W_center = float(W_prof[0]) if len(W_prof)>0 else float("nan")
        profile = {"r": r_prof, "m": m_prof, "P_geom": P_prof_geom, "eps_grav": eps_prof_geom, "W_prof": W_prof}
    else:
        profile = None
        # Minimal WFaktor estimate (center only) when profile is not stored.
        eps_vac_geom = (sigma_vac*chi_vac*screening_factor) * P_to_geom
        W_max = float(np.abs(eps_vac_geom) / (np.abs(eps0 + P0) + 1e-99))
        W_center = W_max

    return {
        "rho_c": rho_c_cgs,
        "M_msun": m/Msun_geom_cm,
        "R_km": R/1e5,
        "Lambda": Lambda,
        "C": C,
        "k2": k2,
        "profile": profile,
        "W_max": W_max,
        "W_center": W_center,
    }


def adaptive_scan_for_target(eos: EOS, target_M: float, *, sigma_vac: float, chi_vac: float, screening_factor: float,
                             include_in_gravity: bool, n_points: int, log10_rho_min: float = 14.2, log10_rho_max: float = 15.9,
                             max_expansions: int = 6):
    """Scan central densities and (if needed) expand the range until the sequence brackets target_M.
    Returns dataframe and a small dict with bracketing diagnostics.
    """
    diag = {"bracketed": False, "log10_rho_min": log10_rho_min, "log10_rho_max": log10_rho_max, "expansions": 0}
    for _ in range(max_expansions):
        rhos = np.logspace(log10_rho_min, log10_rho_max, n_points)
        rows=[]
        for rc in rhos:
            res = integrate_star(eos, rc, sigma_vac=sigma_vac, chi_vac=chi_vac,
                                 screening_factor=screening_factor, include_in_gravity=include_in_gravity)
            if res is not None:
                rows.append(res)
        df = pd.DataFrame(rows)
        if len(df) >= 4:
            mmin, mmax = df.M_msun.min(), df.M_msun.max()
            if (mmin <= target_M <= mmax) and np.isfinite(mmin) and np.isfinite(mmax):
                diag["bracketed"] = True
                break
        # expand range: lower slightly and raise upper
        log10_rho_min = max(13.8, log10_rho_min - 0.15)
        log10_rho_max = min(16.2, log10_rho_max + 0.15)
        diag["expansions"] += 1
    diag["log10_rho_min"] = log10_rho_min
    diag["log10_rho_max"] = log10_rho_max
    return df, diag

def scan_eos(eos: EOS, *, sigma_vac: float, chi_vac: float, screening_factor: float,
            include_in_gravity: bool, n_points: int = (10 if FAST_CI else 18),
            target_M: float = 1.4):
    """Generate an M–R–Λ sequence by scanning central density.

    Key fix (reviewer-critical): I adaptively expand the density range until the sequence brackets `target_M`,
    to avoid NaN entries for R(target_M), Λ(target_M) when the scan range misses the 1.4 M_sun point.
    """
    df, diag = adaptive_scan_for_target(
        eos, target_M,
        sigma_vac=sigma_vac, chi_vac=chi_vac,
        screening_factor=screening_factor, include_in_gravity=include_in_gravity,
        n_points=n_points
    )
    df.attrs["scan_diag"] = diag
    return df

def interp_at_mass(df: pd.DataFrame, target: float = 1.4):
    """Interpolate R and Λ at a target mass.

    Returns (R_km, Lambda, status_string).

    Conservative branch selection:
      A full TOV sequence can become non-monotonic in M(ρ_c) on the unstable
      branch. Sorting by mass alone can therefore mix stable/unstable points and
      yield misleading values for radius-sensitive observables (especially Λ).

      When a central-density column is available I:
        1) sort by ρ_c,
        2) truncate at the first global maximum of M (stable branch),
        3) enforce monotonic increase of M on that branch,
        4) interpolate R(M) and Λ(M) on the remaining points.
    """
    d = df.copy()

    rho_col = None
    for c in ("rho_c_gcm3", "rho_c", "rho_c_cgs"):
        if c in d.columns:
            rho_col = c
            break

    if rho_col is not None:
        d = d.sort_values(rho_col)
        i_peak = int(np.argmax(d.M_msun.values))
        d = d.iloc[: i_peak + 1]
        # enforce monotonic M
        keep = [0]
        Mv = d.M_msun.values
        for i in range(1, len(d)):
            if Mv[i] > Mv[keep[-1]]:
                keep.append(i)
        d = d.iloc[keep]
    else:
        d = d.sort_values("M_msun")

    if len(d) < 4:
        return np.nan, np.nan, "insufficient_points"

    mmin, mmax = float(d.M_msun.min()), float(d.M_msun.max())
    if not (mmin <= target <= mmax):
        return np.nan, np.nan, f"target_out_of_range: [{mmin:.3f},{mmax:.3f}]"

    R = np.interp(target, d.M_msun.values, d.R_km.values)
    L = np.interp(target, d.M_msun.values, d.Lambda.values)
    return float(R), float(L), "ok"

def run_canonical(outdir: str = "outputs", *, sigma_legacy: float = 0.0, chi_legacy: float = 0.0, sigma_vac: float = 0.0, chi_vac: float = 0.0, screening_factor: float = 1.0, include_in_gravity: bool = False):
    import pathlib, matplotlib.pyplot as plt
    outpath = pathlib.Path(outdir)
    outpath.mkdir(parents=True, exist_ok=True)

    eos_list = [
        # Realistic piecewise-polytrope parameterizations (Read et al. 2009; see ppeos_tables reference in Appendix A).
        make_piecewise_eos(34.384, 3.005, 2.988, 2.851, "SLy-PP(Read2009)"),
        make_piecewise_eos(34.269, 2.830, 3.445, 3.348, "AP4-PP(Read2009)"),
        make_piecewise_eos(34.669, 2.909, 2.246, 2.144, "H4-PP(Read2009)"),
        make_piecewise_eos(34.495, 2.921, 3.132, 2.995, "MPA1-PP(Read2009)"),
        make_piecewise_eos(34.031, 2.628, 2.885, 2.951, "WFF1-PP(Read2009)"),
        # Toy EOS for diagnostics / coverage
        make_polytrope_eos(K=3.0e5, Gamma=2.0, name="Poly2(toy)"),
    ]

    summary=[]
    for eos in eos_list:
        for label, (s, ch, inc_g) in [("A_baseline", (0.0, 0.0, False)), ("B_legacy", (sigma_legacy, chi_legacy, False)), ("C_sigma_chi", (sigma_vac, chi_vac, False)), ("D_sigma_chi_gravity", (sigma_vac, chi_vac, True))]:
            df = scan_eos(eos, sigma_vac=s, chi_vac=ch, screening_factor=screening_factor, include_in_gravity=inc_g)
            run_dir = outpath/eos.name/label
            run_dir.mkdir(parents=True, exist_ok=True)
            df.to_csv(run_dir/"mr_lambda.csv", index=False)

            plt.figure()
            plt.plot(df.R_km, df.M_msun)
            plt.xlabel("R [km]"); plt.ylabel("M [Msun]")
            plt.title(f"{eos.name} {label}")
            plt.grid(True, ls=":")
            plt.tight_layout()
            plt.savefig(run_dir/"mr.png", dpi=150)
            plt.close()

            Mmax=float(df.M_msun.max())
            Rmax=float(df.loc[df.M_msun.idxmax(),"R_km"])
            Wmax=float(df.loc[df.M_msun.idxmax(),"W_max"]) if "W_max" in df.columns else float("nan")
            R14,L14,status14 = interp_at_mass(df,1.4)
            scan_diag = getattr(df, "attrs", {}).get("scan_diag", {})
            summary.append({"EOS":eos.name,"case":label,"sigma_vac":s, "chi_vac":ch, "inc_g":inc_g, "screening_factor":screening_factor,"Mmax":Mmax,"R_Mmax":Rmax,"R_1.4":R14,"Lambda_1.4":L14,"W_max":Wmax,"status_1.4":status14,"scan_bracketed":scan_diag.get("bracketed",None),"scan_log10_rho_min":scan_diag.get("log10_rho_min",None),"scan_log10_rho_max":scan_diag.get("log10_rho_max",None),"scan_expansions":scan_diag.get("expansions",None)})

    summary_df = pd.DataFrame(summary)
    summary_df.to_csv(outpath/"summary_canonical_runs.csv", index=False)

    # sensitivities from baseline -> sigma_chi (finite difference per Δsigma, holding chi fixed)
    sens=[]
    for eosname in summary_df.EOS.unique():
        sub=summary_df[summary_df.EOS==eosname].set_index("case")
        if "A_baseline" in sub.index and "C_sigma_chi" in sub.index:
            d=float(sub.loc["C_sigma_chi","sigma_vac"] - sub.loc["A_baseline","sigma_vac"])
            for obs in ["Mmax","R_1.4","Lambda_1.4"]:
                a=sub.loc["A_baseline",obs]
                c=sub.loc["C_sigma_chi",obs]
                if np.isfinite(a) and np.isfinite(c) and d!=0:
                    sens.append({"EOS":eosname,"obs":obs,"S_obs_per_sigma":float((c-a)/d),"sigma_span":d})
    pd.DataFrame(sens).to_csv(outpath/"sensitivities_from_canonical.csv", index=False)

    return summary_df

# --- Diagnostics helpers (used for CI artefacts and reviewer plots) ---
class solve_star:
    @staticmethod
    def scan_family(eos, *, sigma_vac, chi_vac, screening_factor, include_in_gravity,
                    n_points=None, rtol=1e-8, atol=1e-10, store_profiles=False):
        """Scan a central-density ladder to build a mass-radius family.
        If store_profiles=True, returns a list of dict profiles in attribute _profiles on the returned DataFrame.
        """
        import numpy as _np
        import pandas as _pd
        # Use same ladder as scan_eos but with optional n_points override
        if n_points is None:
            n_points = 10 if FAST_CI else 18
        rho_cs = _np.logspace(14.2, 15.6, n_points)  # in g/cm^3 scale proxy
        rows=[]
        profiles=[]
        for rho_c in rho_cs:
            res = integrate_star(eos, rho_c, sigma_vac=sigma_vac, chi_vac=chi_vac, screening_factor=screening_factor,
                                    include_in_gravity=include_in_gravity, rtol=rtol, atol=atol, store_profile=store_profiles)
            rows.append(res)
            if store_profiles:
                profiles.append(res.get('profile'))
        df = _pd.DataFrame(rows)
        if store_profiles:
            df._profiles = profiles  # type: ignore
        return df

def pick_star_by_mass(df, target_mass):
    """Pick the stored profile closest to target_mass from a scan_family() DataFrame."""
    import numpy as _np
    masses = df["M_msun"].to_numpy()
    i = int(_np.argmin(_np.abs(masses - target_mass)))
    try:
        prof = df._profiles[i]  # type: ignore
        return prof
    except Exception:
        raise RuntimeError("No stored profiles found. Call scan_family(..., store_profiles=True).")