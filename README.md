# SFST neutron-star (TOV) reproducibility pack

This repository accompanies the CQG submission **“Vacuum-induced inertial renormalization in neutron-star structure”** and provides a compact, fully reproducible workflow to generate the key numerical artefacts (tables + figures) reported in the manuscript and Supplement.

## What you can reproduce

- Canonical TOV+Love-number runs and derived observables (M–R–Λ) for the headline settings (**Variant A**, default).
- EOS / prior sanity checks (bracketing EOS set + narrow/wide prior).
- Numerical validation artefacts for **Fig. X** (convergence ladder, epsratio distribution, Richardson trace).
- A minimal **GW170817 reweighting demonstrator** that shows how observational data can discriminate scenarios.

## Quick start (local)

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
make run-all
```

Outputs are written to `outputs/` and `figures/`.

## Quick start (Docker)

```bash
docker build -t sfst-cqg .
docker run --rm -v "$PWD/outputs:/work/outputs" -v "$PWD/figures:/work/figures" sfst-cqg
```

## Manuscript artefacts

- `manuscript.docx` — submission manuscript
- `supplement/` — Supplement + diagnostic dossiers and EOS/prior sanity material

## Data & code availability (pinned provenance)

For the exact snapshot identifiers (Docker digest, git/archival commit-equivalent, RNG seed, snapshot IDs) and the one-command reproduction lines, see:

- `DATA_CODE_AVAILABILITY.md`
- `PROVENANCE.md`

## Notes on modelling variants

The paper’s headline results use **Variant A** (inertial-only insertion). **Variant B** is retained strictly as an exploratory sensitivity toggle and is documented in the Supplement.

