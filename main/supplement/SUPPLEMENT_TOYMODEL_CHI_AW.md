# Supplement Sx — Toy model calibration for susceptibility χ and Ambjørn–Watabiki motivation

This supplement section supports the **SFST/QFIS narrative as an interpretative hypothesis** by providing a *minimal, reproducible* toy model
that yields an explicit susceptibility scaling and a practical mapping for scans. It is **not** used to derive the headline EFT/TOV results.

## Sx.1 Toy stochastic flux model (Ornstein–Uhlenbeck flux)

We model the local quantum flux \(\Phi_Q\) as a stationary Ornstein–Uhlenbeck (OU) process with update rate \(\Gamma\):
\[
\dot\Phi_Q(t)= -\Gamma\,\Phi_Q(t) + \eta(t),
\]
where \(\eta\) is a zero-mean Gaussian noise. The retarded response of \(\Phi_Q\) to a slow source \(J\) is
\[
\tilde\chi_{\Phi}(\omega)=\frac{1}{\Gamma-i\omega}.
\]
In linear response, integrating out the flux generates a retarded kernel \(K_R(\omega)\) for the slow matter mode.
A low-frequency expansion defines the induced inertial parameter
\[
K_R(\omega)=K_R(0)+\tfrac12 m_{\rm vac}\,\omega^2+\mathcal O(\omega^4),
\qquad
m_{\rm vac}\equiv \left.\frac{\mathrm d^2 K_R}{\mathrm d\omega^2}\right|_{\omega=0}.
\]
For the OU model, the curvature of the real part of \(\tilde\chi_{\Phi}(\omega)\) yields the characteristic inverse-\(\Gamma\) scaling,
consistent with the working mapping in the main text (up to order-one conventions),
\[
m_{\rm vac}\sim g^2\,\chi/\Gamma.
\]

### Reproducible artefacts
We provide a small deterministic script that evaluates the OU susceptibility and a proxy kernel-curvature mapping:

- Script: `scripts/toy_model_chi_ou.py`
- CSV output: `outputs/toy_model_chi/chi_toy_scan.csv`
- Figure: `figures/toy_model_chi/chi_toy_scaling.png` (and `.pdf`)

These artefacts demonstrate the **parametric dependence** and motivate explicit \((g,\Gamma)\) scans in the repository.

## Sx.2 Ambjørn–Watabiki connection: what is used and what is conjecture

The Ambjørn–Watabiki program on **dynamical triangulations / fractal quantum geometry** motivates the *possibility* that microscopic topology
can modify local mode density and response functions. In this work we use this connection **only as qualitative motivation** for allowing \(\chi\)
to be a slowly varying susceptibility parameter. We **do not** import a specific quantitative value of \(\chi\) from that literature.

Accordingly:
- **Used (minimal)**: the idea that discrete/fractal microstructure can alter effective response functions (mode density, connectivity factors).
- **Conjecture (flagged)**: any direct numerical mapping from a specific triangulation ensemble to \(\chi\) for neutron-star conditions.

Key background references:
- Ambjørn & Watabiki, *Scaling in quantum gravity* (Nucl. Phys. B **445**, 1995).
- Ambjørn, Jurkiewicz & Watabiki, *On the fractal structure of 2D quantum gravity* (Nucl. Phys. B **454**, 1995).

## Sx.3  Ambjørn–Watabiki connection: precise scope and conjecture label

**What we use (strictly qualitative).** The Ambjørn–Watabiki line of work on dynamical triangulations provides concrete examples where a *microscopic, discrete* geometry exhibits nontrivial effective dimensionality and connectivity (often discussed in terms of fractal/branched structure). We use this only as **motivation** for the statement that a vacuum “substrate” with nontrivial micro‑topology can modify the scaling of linear‑response quantities such as an effective susceptibility \(\chi\). citeAmbjornWatabiki1995AmbjornJurkiewiczWatabiki1995

**What we do *not* claim (explicit conjecture).**
- We do **not** derive neutron‑star scale \(\chi\) from dynamical triangulations, nor do we assert that the microscopic topology realized in those models is the correct description of our physical vacuum.
- We do **not** import any quantitative exponents from Ambjørn–Watabiki into the headline EFT/TOV analysis.
- Any mapping from micro‑topology to a specific \(\chi\) normalization is treated as a **conjecture** and is kept in the Supplement.

**Why it is still useful.** The toy OU‑flux model in this supplement demonstrates how an update‑rate scale \(\Gamma\) and a response amplitude \(\chi\) naturally appear in a linear‑response kernel. The Ambjørn–Watabiki motivation is used only to justify exploring \(\chi\) as a slowly varying, topology‑dependent parameter in future work, *not* to support current headline claims.

## Sx.4 Variant B bookkeeping reminder

Variant A corresponds to an inertial renormalization operator and is treated as the controlled baseline. Variant B requires an **independent** matching coefficient for the source operator unless derived otherwise; we therefore keep Variant B as `B_exploratory` and report it side-by-side only as a sensitivity check.
