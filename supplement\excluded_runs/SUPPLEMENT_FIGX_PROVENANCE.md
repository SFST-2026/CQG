Supplementary Note: Figure X data products and plotting provenance
------------------------------------------------------------------

This supplement accompanies Figure X (numerical validation summary). It provides:

1) Raw tables for convergence ladder and Richardson extrapolation:
   - data/<your_run>/convergence.csv  (schema matches data/examples/convergence.csv)

2) epsratio diagnostics summary:
   - data/<your_run>/epsratio_summary.csv  (schema matches data/examples/epsratio_summary.csv)

3) Solver residual traces:
   - data/<your_run>/residual_traces.h5  (schema matches data/examples/residual_traces.h5)

4) Plotting code:
   - scripts/plot_figureX.py (Matplotlib only)

5) Provenance:
   - plot_metadata.json.template in repo root (fill placeholders before archiving)
   - figures/plot_metadata.json generated automatically during plotting

Notes
-----
- Docker digest, git commit, and seed should be recorded in plot_metadata.json (not the manuscript caption).
- The manuscript caption refers to this supplement for full provenance and raw tables.

## Provenance Summary (template)

Repository: Repository: (submission snapshot; public URL will be added upon release)

Git commit: c04378d8b099

Docker image: Docker image: (see PROVENANCE.txt; public image tag will be added upon release)

Docker SHA256 digest: c18878630415a7e3598158d560cf7e615dba8967bdc8283472a610a7e362bedc

Execution seed: 123456

Data snapshot ID(s): data/snapshots/snapshot_c04378d8b099.tar.gz

Plot script: scripts/plot_figureX.py

Plot metadata: figures/plot_metadata.json

Notes on excluded runs: For each excluded/diagnostic run include `diagnosis.txt` with run id, reason for exclusion, epsratio summary, and a link to raw outputs (see `supplement/excluded_runs/INDEX.md`).

### Reproduction commands (example)

```bash
# Pull exact Docker image by digest
docker pull ghcr.io/sfst-qfis/sfst-qfis@sha256:c18878630415a7e3598158d560cf7e615dba8967bdc8283472a610a7e362bedc

# Run container, mount data and produce FigX outputs
docker run --rm -v /path/to/data:/data -v /path/to/output:/out \
  ghcr.io/sfst-qfis/sfst-qfis@sha256:c18878630415a7e3598158d560cf7e615dba8967bdc8283472a610a7e362bedc \
  /bin/bash -lc "cd /workspace && \
  git checkout c04378d8b099 && \
  python scripts/plot_figureX.py --data /data/figX_inputs/ --out /out/figX/ --seed 123456 --emit-panels-only"
```

### plot_metadata.json (one-line template)

```json
{"figure":"FigX","panels":["convergence","epsratio_hist","richardson_trace"],"git_commit":"c04378d8b099","docker_digest":"sha256:c18878630415a7e3598158d560cf7e615dba8967bdc8283472a610a7e362bedc","seed":"123456","data_files":["data/figX_inputs/convergence.csv","data/figX_inputs/epsratio_summary.csv","data/figX_inputs/residual_traces.h5"],"script":"scripts/plot_figureX.py","created_by":"Author Name","created_on":"YYYY-MM-DD"}
```
