# Data and code availability

All code and derived numerical artefacts needed to reproduce the figures and tables in the accompanying manuscript are provided in this repository.

## Pinned provenance for the submission snapshot

- **Archive ID (commit-equivalent for this bundle):** `5af6ad306d4708984415636bdf8b4a5fff1cb23b`
- **Docker image digest:** `sha256:c18878630415a7e3598158d560cf7e615dba8967bdc8283472a610a7e362bedc`
- **Execution seed:** `123456`
- **Data snapshot:** `data/snapshots/snapshot_c04378d8b099.tar.gz`

## Reproducing the main artefacts

### Local (Python)

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
make run-all
```

### Docker (exact image by digest)

```bash
docker build -t sfst-cqg .
# (Optional) if you publish an image, pull by digest:
# docker pull ghcr.io/<org>/<image>@sha256:c18878630415a7e3598158d560cf7e615dba8967bdc8283472a610a7e362bedc

docker run --rm -v "$PWD/outputs:/work/outputs" -v "$PWD/figures:/work/figures" sfst-cqg
```

## Repository contents

- `scripts/` — entrypoints used to generate tables/figures
- `figures/` — figure outputs and plot metadata
- `outputs/` — raw CSV outputs and diagnostics
- `supplement/` — Supplement and diagnostic dossiers (excluded/diagnostic runs), including run IDs and links to raw outputs

For full details (including run IDs for excluded/diagnostic cases), see `PROVENANCE.md`.
