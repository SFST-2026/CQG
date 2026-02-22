# Compact diagnostic table for flagged rows (template)

This table is intended to summarize every run flagged as DIAGNOSTIC (e.g., δ_total>50% or failed convergence).

| run_id | EOS | case_tag | status | triggered_rules | action_taken | outcome | diagnostics_path |
|---|---|---|---|---|---|---|---|
|  |  |  |  |  |  |  | outputs/diagnostics/<run_id>/ |


We generate the machine‑readable source for this table from outputs/audit_trail.csv.
