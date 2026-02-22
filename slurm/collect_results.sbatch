#!/bin/bash
#SBATCH --job-name=collect_sfst
#SBATCH --output=slurm_logs/collect_%j.out
#SBATCH --time=00:30:00
#SBATCH --mem=4G
#SBATCH --cpus-per-task=1
#SBATCH --partition=standard

set -euo pipefail

# ====== EDIT THIS PATH ======
WORKDIR=/home/youruser/projects/sfst_repo   # <-- set to your repo path
# ===========================

cd "${WORKDIR}"

python - <<'PY'
import json, glob, os
import pandas as pd

rows=[]
audit=[]
for p in sorted(glob.glob("outputs/diagnostics/*/summary.json")):
    run_dir=os.path.dirname(p)
    try:
        d=json.load(open(p))
        rows.append(d)
        status = "FAILED" if not d.get("converged", False) else "DONE"
        reason = d.get("error","")
        audit.append({
            "run_id": d.get("run_id", os.path.basename(run_dir)),
            "eos": d.get("eos"),
            "sigma": d.get("sigma"),
            "status": status,
            "reason": reason,
            "path": run_dir
        })
    except Exception as e:
        audit.append({
            "run_id": os.path.basename(run_dir),
            "eos": None,
            "sigma": None,
            "status": "PARSE_ERROR",
            "reason": str(e),
            "path": p
        })

df = pd.DataFrame(rows)
df.to_csv("outputs/scan_grid.csv", index=False)

df_a = pd.DataFrame(audit)
df_a.to_csv("outputs/audit_index.csv", index=False)

print("Wrote outputs/scan_grid.csv with", len(df), "rows")
print("Wrote outputs/audit_index.csv with", len(df_a), "rows")
PY
