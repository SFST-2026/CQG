all: pdf html

pdf:
	python3 build_manuscript.py

html:
	python3 build_manuscript.py

clean:
	rm -f manuscript.pdf manuscript.html

# --- CQG release helpers (chosen default workflow) ---

DOCKER_IMAGE ?= sfst-qfis:local

.PHONY: docker_build figX figures provenance sha256sums sanity release run
.NOTPARALLEL: release

docker_build:
	@echo "Building Docker image $(DOCKER_IMAGE)"
	docker build -t $(DOCKER_IMAGE) .

figX:
	@mkdir -p figures
	python3 scripts/plot_figureX.py --data-dir data/examples --out-dir figures --observable Lambda14 --dpi 600 --emit-panels-only

figures: figX
	@echo "Figures written to ./figures"

provenance:
	python3 scripts/update_provenance.py --docker-image $(DOCKER_IMAGE)

sha256sums:
	bash scripts/make_sha256sums.sh

sanity:
	@echo "Running quick sanity demos (lightweight)"
	@mkdir -p outputs/sanity
	python3 scripts/gw170817_reweight_demo.py \
		--posterior data/examples_gw/gw170817_like_posterior.csv \
		--sigma 0.02 \
		--out outputs/sanity/gw170817_demo.csv || true
	python3 scripts/prior_sanity_demo.py --out outputs/sanity/prior_demo.csv || true


run:
	@echo "Running canonical runs (default dry-run unless SFST_DRYRUN=0)."
	@SFST_DRYRUN=$${SFST_DRYRUN:-1} python3 scripts/run_canonical_runs.py --out-dir outputs/canonical_runs || true

# Full pipeline helper (matches README quick-start)
run-all:
	@echo "Running full pipeline (scripts/run_all.py)"
	python3 scripts/run_all.py

# One-command release step: (re)build FigX panels, stamp commit/digest/seed, refresh checksums.
release:
	@echo "Release: run -> figures -> provenance stamp -> checksums -> sanity"
	@$(MAKE) run
	@$(MAKE) figX
	@$(MAKE) provenance
	@$(MAKE) sha256sums
	@$(MAKE) sanity
	@echo "Release OK: manuscript.docx stamped; plot_metadata.json + outputs/provenance.* updated."

.PHONY: scan_gGamma_small params_minimal

params_minimal:
	@cp -f slurm/params_minimal.csv params.csv || true
	@echo "Wrote params.csv from slurm/params_minimal.csv"

scan_gGamma_small:
	@echo "Running small (g,Gamma) scan smoke test. Set SFST_DRYRUN=0 to use a real solver."
	@SFST_DRYRUN=$${SFST_DRYRUN:-1} python3 scripts/scan_gGamma_small.py

# Build compact EOS/prior sanity table for Supplement
sanity_table:
	@echo "Building EOS/Prior sanity grid (requires outputs/runs_summary.csv)"
	@if [ ! -f outputs/runs_summary.csv ]; then \
		echo "outputs/runs_summary.csv not found; generating it via scripts/build_runs_summary.py"; \
		python3 scripts/build_runs_summary.py; \
	fi
	python3 scripts/build_eos_prior_sanity_table.py --runs-summary outputs/runs_summary.csv

validate_plot_metadata:
	python scripts/validate_plot_metadata.py --allow-placeholders