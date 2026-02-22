# Poly2/NaN stress-test dossier summary and headline-bias check

## Purpose
Poly2toy (and similar toy/stress-test cases) are **excluded from headline claims** and retained only as numerical
stress-tests. This note provides a **reproducible check** demonstrating that these exclusions do not bias the
headline statistics used in the manuscript.

## Where Poly2 dossiers live
Poly2 dossiers are referenced from the excluded-runs index and may be stored under:

- `supplement/excluded_runs/Poly2toy_*`  (preferred)
- `outputs/diagnostics/Poly2toy_*`       (raw diagnostic artefacts)

Some ZIP bundles created on Windows may contain literal backslashes in directory names. The tooling in this repo
tries to handle both layouts.

## Run the headline-bias check
```bash
make headline_bias_check
```

Outputs:
- `outputs/headline_bias_check.md`
- `outputs/headline_bias_check.json`

Interpretation: headline tables are computed from the **headline set** (canonical EOS, Variant A, non-excluded, non-stress-test).
If `Δmean`/`Δmedian` in the report are ~0 (within numerical noise), then exclusions (including Poly2 NaNs) do not bias headline claims.

## Why Poly2toy can generate NaNs
Poly2toy is a deliberately aggressive stress-test EOS. For certain parameter combinations it can push the integration outside
the perturbative/stability regime and trigger solver breakdowns (NaNs). These cases are informative for mapping failure boundaries,
but they are not physically interpretable as headline predictions.
