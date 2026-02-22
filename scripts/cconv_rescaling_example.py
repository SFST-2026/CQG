import os
import sys

# Ensure repo root is importable when this script is executed as a file.
_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

import pandas as pd
from pathlib import Path

# Demonstrate kernel normalization rescaling:
# If K_R -> α K_R, then Σ'' -> α Σ'' and therefore σ -> α σ (if χ fixed), so observables shift linearly in σ (to first order).
# Using measured sensitivities S_obs_per_sigma, I can propagate.

def main(alpha=2.0):
    out = Path("outputs")
    sens = pd.read_csv(out/"sensitivities_from_canonical.csv")
    # choose reference sigma span = 0.06 (as in canonical)
    sigma_ref = 0.06
    # predicted observable shift under σ -> α σ : ΔO_new ≈ S * (α sigma_ref) and ΔO_ref ≈ S * sigma_ref
    sens["alpha"] = alpha
    sens["sigma_ref"] = sigma_ref
    sens["DeltaO_ref"] = sens["S_obs_per_sigma"] * sigma_ref
    sens["DeltaO_rescaled"] = sens["S_obs_per_sigma"] * (alpha*sigma_ref)
    sens["scale_factor"] = alpha
    sens.to_csv(out/"cconv_rescaling_example.csv", index=False)
    print(sens)

if __name__ == "__main__":
    main(alpha=2.0)
