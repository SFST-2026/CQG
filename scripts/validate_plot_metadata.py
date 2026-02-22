#!/usr/bin/env python3
"""Validate plot_metadata.json structure and (optionally) ensure no placeholder tokens remain."""

import argparse, json, sys, re, pathlib

PLACEHOLDER_RE = re.compile(r"<<[^>]+>>|<[^>]+>")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--path", default="figures/plot_metadata.json")
    ap.add_argument("--allow-placeholders", action="store_true",
                    help="Allow placeholder tokens (useful before final release stamping).")
    args = ap.parse_args()

    p = pathlib.Path(args.path)
    if not p.exists():
        print(f"ERROR: {p} not found", file=sys.stderr)
        return 2

    data = json.loads(p.read_text(encoding="utf-8"))
    required = ["figure","panels","git_commit","docker_digest","seed","data_files","script"]
    missing = [k for k in required if k not in data]
    if missing:
        print("ERROR: missing keys:", missing, file=sys.stderr)
        return 2

    txt = json.dumps(data)
    if (not args.allow_placeholders) and PLACEHOLDER_RE.search(txt):
        print("ERROR: placeholder tokens found in plot_metadata.json (run make release/provenance stamping).", file=sys.stderr)
        return 3

    print("OK: plot_metadata.json validated.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
