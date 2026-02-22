# Table notes (outliers, plausibility, and formatting)

## Extreme uncertainty rows (e.g., delta_disc > 100%)
If we see delta_disc or delta_total above 100% (often for Lambda on specific EOS), we treat the run as a numerical outlier until I can show convergence. We keep the row in the Supplement with a footnote and a diagnostic link, and I exclude it from headline summary tables.

## Non-monotonic changes (example: H4 Variant-B R1.4 jump)
Variant B changes the insertion semantics and can produce non-monotonic responses because it modifies both inertia and the gravitational source. We therefore do not interpret Variant-B-only deviations as physical predictions; I present them as sensitivity-only and I require diagnostics (residuals, Richardson, WFaktor) to confirm they are at least numerically stable.

## Presentation standardization
- I include units in every table header: Mmax [Msun], R1.4 [km], Lambda1.4 [-], deltas [%].
- we use consistent significant figures across columns.
- I explicitly mark Lambda1.4 as dimensionless.
