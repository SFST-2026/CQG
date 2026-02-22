# Formal Appendix — EFT matching, power counting, and operator bookkeeping

This appendix is reader-facing: it isolates the EFT assumptions and *bookkeeping* used to interpret the regulator scan results.

## A.1  What is being matched?
We consider a low-energy description of neutron-star structure in GR (TOV) augmented by vacuum-induced inertial terms.
The numerical pipeline treats the vacuum contribution as an *effective local insertion* parameterized by a dimensionless
regulator amplitude **σ** and an inertial susceptibility **χ**, combined as

- **m_vac(r) = σ χ · m_ref(r)**  (convention; see `CONVENTIONS.md`)

where *m_ref(r)* is the reference inertial mass-density scale used in the TOV integration.

**Variant A (baseline, interpretable):** insertions enter the *inertial* sector only (schematically ε+P → ε+P+m_vac).

**Variant B (exploratory):** the same insertion is additionally fed into the *source* sector (schematically ε → ε+δ ε_vac).
This is marked `variant=B_exploratory` because, without an independent operator coefficient on the source-side insertion,
it can represent **double counting** of the same EFT effect.

## A.2  Power counting and “smallness” diagnostics
We use the local diagnostic

- **epsratio(r) = ε_vac,inertial(r) / ε_ref(r)**

and interpretability bands on **max_r |epsratio|**:
- ≤ 0.10 (perturbative / interpretable)
- 0.10–0.30 (stress test / sensitivity context)
- > 0.30 (diagnostic or excluded)

A quantified scaling example is given in Footnote 1 of the main manuscript:
δΛ/Λ ≈ 2.5 · epsratio (conservative central values).

## A.3  Operator bookkeeping and Variant-B double counting
A minimal bookkeeping that avoids double counting is:

- treat inertial and source insertions as **distinct operators** with distinct Wilson coefficients (c_I, c_S)
- Variant A corresponds to c_I ≠ 0, c_S = 0
- Variant B sets c_I = c_S by construction, which is **not** guaranteed by EFT and is therefore exploratory

In the supplement we provide a “paired” ΔΛ(σ) comparison panel (`figures/variantA_vs_B_exploratory_deltaLambda_sigma_panel.*`)
that empirically shows Variant B tends to increase |ΔΛ| relative to Variant A at fixed σ, consistent with a double-counting tendency.

## A.4  Reproducibility pointers
- Machine-readable headline tables: `outputs/headline_with_diagnostics.csv`, `outputs/headline_without_diagnostics.csv`
- Audit index and trail: `outputs/audit_index.csv`, `outputs/audit_trail.csv`
- Per-run diagnostics: `outputs/diagnostics/<run_id>/diagnosis.txt`



---

## A.7  SFST/QFIS linear-response mapping (interpretative hypothesis)

**Status (scope):** This section provides *interpretative scaffolding* only. Headline numerical claims in the paper remain based on the EFT/TOV pipeline and audited diagnostics. SFST/QFIS content is offered as a physically motivated organizing principle and a set of testable follow-ups.

### A.7.1  Low-frequency EFT matching and the definition of \(m_{\mathrm{vac}}\)
Start from a slow collective matter mode \(x(t)\) coupled to a stochastic quantum flux \(\Phi_Q\):

\[
S_{\mathrm{int}} = \int d^4x\; g\, \Phi_Q(x)\,\mathcal{O}[\psi(x)].
\]

Integrating out fast flux degrees of freedom yields a retarded kernel \(K_R(\omega)\) for the slow matter mode,

\[
S_{\mathrm{eff}}[x] = \tfrac12\int\frac{d\omega}{2\pi}\; x(-\omega)\,K_R(\omega)\,x(\omega) + \cdots.
\]

In the low-frequency regime \(\omega\ll \Lambda_{\rm micro}\), expand

\[
K_R(\omega)=K_R(0)+\tfrac12 m_{\mathrm{vac}}\,\omega^2+\mathcal{O}(\omega^4),
\qquad
m_{\mathrm{vac}}\equiv \left.\frac{d^2K_R}{d\omega^2}\right|_{\omega=0}.
\]

At leading order in \(g\), linear response gives \(K_R(\omega)\supset g^2\,\tilde\chi(\omega)\), where \(\tilde\chi\) is the retarded susceptibility of the flux operator coupled to \(\mathcal{O}\). Hence

\[
m_{\mathrm{vac}}\simeq g^2\left.\frac{d^2\tilde\chi(\omega)}{d\omega^2}\right|_{\omega=0}.
\]

Model \(\tilde\chi\) as a causal response with a characteristic update rate (width) \(\Gamma\) and a dimensionless susceptibility \(\chi\); up to order-one conventions this yields the working scaling

\[
m_{\mathrm{vac}}\sim \frac{g^2\,\chi}{\Gamma}.
\]

### A.7.2  Power counting and validity
Define \(\epsilon_g\equiv g\) and \(\epsilon_\Gamma\equiv \omega/\Gamma\). The induced inertial term is \(\mathcal{O}(g^2/\Gamma)\). A controlled expansion requires (schematically)

\[
\frac{g^2\chi}{\Gamma}\ll m_{\rm bare},\qquad \epsilon_\Gamma\ll 1,
\]

and higher-order terms \(\mathcal{O}(g^4/\Gamma^2)\) remain parametrically suppressed.

### A.7.3  Operator bookkeeping and Variant B
Variant A corresponds to an inertial renormalization operator (controlled default). A *source insertion* requires an independent EFT operator with its own matching coefficient unless derived otherwise. This is the basis for labeling Variant B as **exploratory** and for reporting it side-by-side (paired figures/tables) rather than using it for headline interpretation.

### A.7.4  Practical mapping used for scans
For explicit \((g,\Gamma)\) scans we use

\[
\sigma\;\equiv\; \frac{g^2}{\Gamma}\,\chi_{\rm ref},
\]

with a fixed reference normalization \(\chi_{\rm ref}=1\) (convention). See `scripts/scan_mapping_sigma_g2_over_Gamma.py` for a repo-integrated scan driver that records diagnostics and exports machine-readable scan tables.

### A.7.5  Ambjørn–Watabiki (context)
We cite Ambjørn–Watabiki as a *motivation* for considering discrete/fractal microscopic topologies where susceptibilities can acquire scale dependence. In this repository, these ideas are not used as inputs to headline claims; they motivate a toy-model extension documented in the Supplement.



## A.6  Operator separation and why Variant B needs an independent matching coefficient (readers-critical)

### A.6.1 Minimal operator basis (schematic)
To avoid double counting, we distinguish **inertial renormalization** from **source insertion** at the EFT level. A minimal schematic basis is:

- **Inertial operator (Variant A, controlled default):**
  \[
  \mathcal L_{\rm eff} \supset c_{\rm inert}\,\Phi_Q\,\mathcal O_{\rm kin}[\psi],
  \]
  whose matching renormalizes the *inertial* response of matter modes and is implemented in the TOV system as the
  replacement \((\varepsilon+P)\to(\varepsilon+P)+\varepsilon_{\rm vac,inertial}\) (code convention).

- **Source operator (Variant B, exploratory):**
  \[
  \mathcal L_{\rm eff} \supset c_{\rm src}\,\Phi_Q\,\mathcal O_{\rm src}[\psi] \;\Rightarrow\; \delta T^{\mu\nu}\neq 0.
  \]
  This operator modifies the gravitational source (schematically \(\rho\to\rho+\delta\rho_{\rm vac}\)). **Unless one derives**
  \(c_{\rm src}=c_{\rm inert}\) from an explicit microscopic model, the two coefficients are *independent matching data*.

**Bookkeeping rule used in this work:** we treat Variant A as the controlled baseline because it corresponds to a single inertial operator.
We keep Variant B only as a **sensitivity check** (`variant=B_exploratory`) and we do **not** use it for headline interpretation.
A readers can therefore read Variant B as: “what would happen if an additional source operator of comparable size existed?”

### A.6.2 Consequence for interpretation
- Headline claims (Abstract/Main) are based on **accepted Variant‑A runs** only (see `outputs/accepted.csv`).
- Variant‑B results are shown **side-by-side** (paired figures/CSVs) to illustrate the scale of possible shifts under an additional operator,
  but are explicitly labelled exploratory because \(c_{\rm src}\) is not matched in the present work.

### A.6.3 Practical implementation note
In the repository, `outputs/runs_summary.csv` contains the explicit variant labels (`A` vs `B_exploratory`). If future work
derives or constrains \(c_{\rm src}\), Variant‑B can be upgraded by scanning \(c_{\rm src}/c_{\rm inert}\) as an additional axis.

## A.7  Operator bookkeeping and Variant‑B gate (concise, auditable)

**Purpose.** This section provides a compact operator bookkeeping and matching prescription that (i) clarifies why *Variant A* (inertial‑only insertion) is the controlled EFT implementation used for headline claims, and (ii) specifies the conditions under which *Variant B* (inertial + source insertion) may be retained **only** with an independent, separately matched source operator.

### Operator basis and notation
- **\(\mathcal{O}_{\rm kin}[\psi]\)**: canonical matter kinetic operator (bare inertia).
- **\(\mathcal{O}_{\rm int}[\psi]\)**: matter operator that couples linearly to the flux \(\Phi_Q\) with coupling \(g\).
- **\(\mathcal{O}_{\rm src}[\psi]\)**: operator that (if present) contributes directly to the gravitational source (stress‑energy) with an *independent* matching coefficient \(c_{\rm src}\).
- Flux degrees of freedom: \(\Phi_Q\) with retarded response \(\tilde\chi(\omega)\) and characteristic update rate \(\Gamma\).

We define the induced inertial parameter via the low‑frequency expansion of the retarded kernel:
\[
K_R(\omega)=K_R(0)+\tfrac12 m_{\rm vac}\,\omega^2+\mathcal{O}(\omega^4),\qquad
m_{\rm vac}\equiv\left.\frac{\mathrm d^2K_R}{\mathrm d\omega^2}\right|_{\omega=0}.
\]

### Matching at leading order (linear response)
Start from a microscopic interaction
\[
S_{\rm int}= g\int\mathrm d^4x\;\Phi_Q(x)\,\mathcal{O}_{\rm int}[\psi(x)].
\]
Integrating out \(\Phi_Q\) at one loop / linear response yields a contribution to the matter kernel
\[
\Delta K_R(\omega)\simeq g^2\,\tilde\chi(\omega)\,F[\mathcal{O}_{\rm int}],
\]
and therefore
\[
m_{\rm vac}\simeq g^2\left.\frac{\mathrm d^2\tilde\chi}{\mathrm d\omega^2}\right|_{\omega=0}\times N\;\approx\; g^2\,\chi/\Gamma,
\]
where \(N\) is a calculable normalization from the projection \(F[\cdot]\), and the last step defines the working \(\chi\) and \(\Gamma\) used in the scans.

### Power counting and consistency
Assign scaling \(g=\mathcal{O}(\epsilon)\), \(\omega/\Gamma=\mathcal{O}(\epsilon_\omega)\). The induced inertial term is \(\mathcal{O}(g^2/\Gamma)\). The EFT expansion is controlled in accepted runs if
\[
g^2/\Gamma\ll m_{\rm bare},
\]
and higher‑order corrections \(\mathcal{O}(g^4/\Gamma^2)\) are numerically subleading (verified empirically by our epsratio / stability diagnostics).

### Variant A vs Variant B (gate)
- **Variant A (controlled default, headline):** insert \(m_{\rm vac}\) **only** in the inertial coupling (hydrostatic balance / enthalpy factor). This directly corresponds to matching \(\mathcal{O}_{\rm int}\) and integrating out \(\Phi_Q\) as above.
- **Variant B (exploratory only):** inserting the *same* coefficient into the gravitational source is EFT‑consistent **only** if a distinct operator
  \[
  S_{\rm src}= c_{\rm src}\int\mathrm d^4x\;\mathcal{O}_{\rm src}[\psi]
  \]
  exists and \(c_{\rm src}\) is obtained by an **independent matching calculation**, *or* if one can prove an operator identity fixing a robust ratio between inertial and source terms.

**Policy used in this repository.** Absent an independent matching for \(c_{\rm src}\), Variant B is labeled `B_exploratory`, reported only in the Supplement, and **excluded from headline statistics**. If Variant B is used for sensitivity checks, we recommend two‑parameter scans in \((g,c_{\rm src})\) rather than setting \(c_{\rm src}=g\) by fiat.
