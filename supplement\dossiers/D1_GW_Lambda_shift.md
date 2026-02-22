# D1 — GW tidal-deformability shift (Λ-Shift test)

## Matching model
For a fixed EOS and within the linearized σ-scan window:
\[
\Lambda_{1.4}(\sigma) \approx \Lambda_{1.4}^{(0)} + S_{\Lambda}(EOS)\,\sigma.
\]
For a GW event with posterior samples for tidal parameters (\(\tilde\Lambda\) or \(\Lambda_{1,2}\)), a first-pass proxy maps:
\[
\sigma \approx \frac{\tilde\Lambda-\Lambda_{1.4}^{(0)}}{S_{\Lambda}(EOS)}.
\]
**Note:** this proxy is conservative and is superseded by the mass-dependent forward model \(\tilde\Lambda(m_1,m_2;\sigma)\) in future work.

## Data provenance (this snapshot)
- GW170817 posterior samples: `data/gw_posteriors/` (imported from released `.dat.gz` samples).
- GW190425 posterior samples: `data/gw_posteriors/` (GWTC PEDataRelease `.h5`).

## σ_req and perturbativity gate
Given an observed shift target \(\Delta\tilde\Lambda_{\mathrm{obs}}\), the implied:
\[
\sigma_{\mathrm{req}} \approx \Delta\tilde\Lambda_{\mathrm{obs}}/S_{\Lambda}.
\]
Accept a claim only if the corresponding run satisfies:
- max|epsratio(r;σ)| ≤ 0.10 (perturbative band), otherwise label as stress/diagnostic.

## Bayes-factor sketch (stacking)
For events \(d_i\) with posteriors \(p(\tilde\Lambda|d_i)\), define a reweighted likelihood in σ:
\[
p(d_i|\sigma) \propto \int p(\tilde\Lambda|d_i)\,\delta(\tilde\Lambda-\tilde\Lambda(\sigma))\,d\tilde\Lambda,
\]
then stack \(\prod_i p(d_i|\sigma)\) with priors on σ and (optionally) on EOS.
If per-sample log-likelihood is available (as in some PEDataRelease files), replace the KDE proxy by the exact likelihood re-evaluation.

## Deliverables in this repo
- Scripts: `scripts/gw_reweight_stack.py`, `scripts/predict_sigma_from_deltaLambda.py`
- Outputs: `artefacts/` (posterior CSV/plots, Bayes-factor text)
