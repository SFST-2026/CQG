# Prioritized pre-submission actions (checklist)

This checklist summarizes the remaining high-leverage actions before submission.

1) **Targeted stabilization re-runs for all δ_total > 50% runs**  
   Use staged grid refinement and stricter tolerances. If not stabilizable, document and **EXCLUDE** with an audit trail.  
   - Controller: `scripts/refine_and_retry.py` (wrapper) or `scripts/refine_and_retry_cli.py` (CLI/Slurm)  
   - Protocol: `README_refinement.md`  
   - Audit index: `outputs/audit_index.csv`

2) **Variant-B gate (EFT consistency)**  
   Add/verify the Methods sentence and Appendix A.7 gate: Variant B only with independently matched source coefficient `c_src`; otherwise `B_exploratory` and Supplement-only.

3) **Main text visibility**  
   Keep the compact sensitivities table (SLy/AP4) and include three representative Richardson plots with Supplement links.

3a) **EOS / prior sensitivity (headline numbers)**
   Ensure the Supplement contains **at least 2–3 representative EOS/prior checks** for the headline results (e.g., SLy/AP4 + one additional representative EOS family or a soft/stiff bracket; plus a narrow vs wide σ-prior sanity overlay for the demo). Missing this is a common reviewer request.

3b) **Provenance completeness (IDs & links)**
   Ensure all provenance fields are complete and cross-linked, especially **data snapshot IDs** (`data/snapshots/snapshot_c04378d8b099.tar.gz.tar.gz`) and any archive identifiers referenced in the manuscript/Supplement. Incomplete IDs often trigger follow-up questions.

4) **Toy-model χ calibration visibility**  
   Ensure Supplement links to: `scripts/toy_model_chi_ou.py` and `figures/toy_model_chi/chi_toy_scaling.png`.

5) **Public archive**  
   Create Git tag and Zenodo DOI; update Data & Code Availability; verify `SHA256SUMS.txt`.
