# Public archiving checklist (to complete before submission)

This repository snapshot is self-contained for review. Before journal submission we will complete *public archiving*:

1. Create and push a release tag, e.g. `v1.0.0-submission`.
2. Create a Zenodo archive from the tagged GitHub release.
3. Insert the Zenodo DOI into the manuscript section **A1b** (Public archiving plan).
4. Verify integrity:
   - regenerate `SHA256SUMS.txt`
   - include the Zenodo record link and the Git commit hash
5. Optional: attach CI artefacts (accepted.csv, diagnostic.csv, audit_trail.csv) to the release.

We do **not** mint a DOI inside this ChatGPT environment; this checklist ensures the step is executed in the real repository.
