# Quick sanity reweighting demo (GW170817)

This repository includes a minimal, fully reproducible reweighting demonstration intended as a **sanity check** for the GW-facing inference hook discussed in the manuscript.

## What it does
- Loads an example posterior sample (`data/examples_gw/gw170817_like_posterior.csv`).
- Applies a simple reweighting step against a parameterized SFST-modified tidal relation (toy model).
- Writes a compact summary (`summary.json`) plus diagnostic plots.

## Run
```bash
python scripts/gw170817_reweight_demo.py \
  --in data/examples_gw/gw170817_like_posterior.csv \
  --out outputs/gw170817_reweight_demo
```

## Expected outputs
- `outputs/gw170817_reweight_demo/summary.json`
- `outputs/gw170817_reweight_demo/reweight_hist.png` (if enabled)

## Provenance
Run `make provenance` (or `make release`) to stamp:
- git commit
- Docker SHA256 digest (if applicable)
- canonical seed

These identifiers are written to `outputs/provenance.json` and to `figures/plot_metadata.json`.
