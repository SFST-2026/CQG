#!/usr/bin/env python3
"""run_tov.py

Small CLI entrypoint used by refinement controllers and Slurm templates.

Expected CLI (used throughout the repo docs):
    python run_tov.py --eos <EOS> --sigma <SIGMA> --run-tag <RUN_TAG> --grid-factor <GRID_FACTOR> --newton-tol <NEWTON_TOL>

This script calls scan_wrappers.compute_tov_case and writes summary.json under
outputs/diagnostics/<run_tag>/ unless an explicit --output-dir is provided.
"""

import argparse
import json
from pathlib import Path

from scan_wrappers import compute_tov_case

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--eos', required=True)
    ap.add_argument('--sigma', required=True, type=float)
    ap.add_argument('--run-tag', required=True, dest='run_tag')
    ap.add_argument('--grid-factor', type=float, default=1.0, dest='grid_factor')
    ap.add_argument('--newton-tol', type=float, default=1e-6, dest='newton_tol')
    ap.add_argument('--timeout', type=int, default=3600)
    ap.add_argument('--output-dir', default=None, help='Optional override for outputs/diagnostics/<run_tag>')
    args = ap.parse_args()

    extra = {'grid_factor': args.grid_factor, 'newton_tol': args.newton_tol}
    res = compute_tov_case(eos=args.eos, sigma=args.sigma, run_tag=args.run_tag, extra=extra, timeout=args.timeout)

    # Write summary.json to the run directory for auditability.
    run_dir = Path(args.output_dir) if args.output_dir else Path('outputs') / 'diagnostics' / args.run_tag
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / 'summary.json').write_text(json.dumps(res, indent=2))
    print(json.dumps(res, indent=2))

if __name__ == '__main__':
    main()
