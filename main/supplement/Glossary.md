# Glossary (compact)

We use the following symbols and conventions throughout the addendum/supplement.

- **σ (sigma)** — Matching coefficient: EFT response coefficient defined by the mapping 
 σ = C_conv · Σ_R''(0) / χ. 
 In my reference conventions σ is dimensionless and acts as a multiplier in the numerical model that controls the amplitude of the vacuum-induced inertial response.

- **χ (chi)** — Normalization factor: inverse mapping factor chosen so that σχ carries mass dimension. In my reference implementation I set χ = 1 (dimensionless stand‑in) and interpret σ per cell.

- **m_vac** — Induced inertial parameter: defined by the kernel expansion 
 K_R(ω) = K_R(0) + (1/2) m_vac ω² + O(ω⁴), 
 so that m_vac ≡ d²K_R/dω²|_{ω=0}. Numerically I have m_vac = σχ under my fixed conventions.

- **m_bare** — SM rest‑mass renormalization: Standard Model renormalized rest mass; I absorb UV divergences and SM counterterms into m_bare(μ) and keep it distinct from m_vac.

- **Σ_R''(0)** — Kernel curvature (matching input): second derivative of the retarded self‑energy at ω = 0; I compute it in regulator schemes (PV, DimReg) and scan the regulator scale to define the envelope used for δσ_match.

- **C_conv** — Convention factor: kernel normalization constant. In this work I fix C_conv = 1; if a reader rescales the kernel by α, then σ → α σ.

- **ε_vac,inertial(r)** — Derived diagnostic: local effective inertial energy density contribution defined as 
 ε_vac,inertial(r) ≡ (σχ S(r)) · ε_ref(r). 
 I report ε_vac,inertial/ε_ref as a plausibility check.

- **Variant A / Variant B** (insertion semantics) — 
 Variant A (default): inertial‑only insertion — m_vac modifies the inertial factor (ε+P) but not the gravitational source dm/dr. 
 Variant B (exploratory): inertial + gravitational‑source insertion — I also add the same correction to dm/dr; we treat Variant B as a sensitivity check only and flag a conceptual double‑counting risk.
