# Supplement S.N — Variant‑B: exploratory note (toy example)

## Purpose
I provide a minimal, formal demonstration of why inserting the same vacuum‑induced inertial coefficient into both the inertial term and the gravitational source can amount to double counting, and I state clear criteria for when Variant‑B is a justified exploratory test.

## Minimal Newtonian toy model
Consider a spherically symmetric, nonrelativistic matter distribution with mass density \(\rho(r)\) and Newtonian potential \(\Phi(r)\) satisfying
\[
\nabla^2\Phi = 4\pi G\,\rho(r).
\]
A pointlike test element of rest mass \(m\) obeys
\[
m_{\rm inert}\,a = -m_{\rm grav}\,\nabla\Phi.
\]
Introduce a vacuum‑induced inertial correction \(m_{\rm vac}\) defined by the low‑frequency EFT matching:
\[
m_{\rm inert} \to m_{\rm inert}+m_{\rm vac}.
\]

## Two insertion choices
**Variant‑A (inertial only).**  
Modify only the inertial coupling:
\[
(m_{\rm inert}+m_{\rm vac})\,a = -m_{\rm grav}\,\nabla\Phi.
\]
The gravitational source \(\rho(r)\) and hence \(\Phi\) remain determined by the original matter distribution.

**Variant‑B (inertial plus source).**  
In addition to the inertial shift, add the same vacuum contribution to the source:
\[
\nabla^2\Phi = 4\pi G\,[\rho(r)+\delta\rho_{\rm vac}(r)],\qquad
(m_{\rm inert}+m_{\rm vac})\,a = -(m_{\rm grav}+\delta m_{\rm vac})\,\nabla\Phi,
\]
where \(\delta\rho_{\rm vac}\) and \(\delta m_{\rm vac}\) are taken proportional to the same matching coefficient.

## Demonstration of double counting
If \(\delta\rho_{\rm vac}\) is constructed from the same EFT operator that produced \(m_{\rm vac}\) without introducing an independent coupling, then the vacuum contribution enters both sides of the dynamical balance. Linearizing for small \(m_{\rm vac}\) shows an additive effect on the acceleration that is the sum of (i) reduced acceleration due to larger inertial mass and (ii) increased gravitational pull due to the extra source. Both effects originate from the same matched coefficient and therefore represent two manifestations of the same physical modification counted twice.

Formally, writing \(\delta\rho_{\rm vac}=\alpha\,m_{\rm vac}\,f(r)\) and \(\delta m_{\rm vac}=\beta\,m_{\rm vac}\) with \(\alpha,\beta\) fixed by the chosen insertion, the net first‑order change in acceleration scales as \((\beta-\alpha)\,m_{\rm vac}\) times the background gradient. If \(\alpha\) and \(\beta\) are not independent EFT parameters, there is no principled way to separate the two contributions.

## EFT consistency condition
A consistent EFT treatment requires that each independent operator in the effective action has its own matching coefficient. If I use the same operator to generate both an inertial renormalization and a source term, Variant‑B must either (i) introduce a distinct operator (and matching procedure) for the source contribution, or (ii) provide a derivation showing that the two insertions are not independent and that their combined effect is the correct single‑counted physical observable. Absent this, Variant‑B is an exploratory reparameterization rather than a physically distinct model.

## Practical reporting policy
I always mark Variant‑B runs explicitly as exploratory (variant=B_exploratory). Headline claims are based on Variant‑A; Variant‑B results are reported only to illustrate sensitivity to the (potentially unjustified) double insertion unless I provide a formal EFT justification with independent operator matching.
