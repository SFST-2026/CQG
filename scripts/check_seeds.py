#!/usr/bin/env python3
import sys, yaml, pathlib

p = pathlib.Path("config/seeds.yaml")
if not p.exists():
    print("config/seeds.yaml missing")
    sys.exit(1)

data = yaml.safe_load(p.read_text())
for k in ["global_seed","numpy_seed","python_random_seed"]:
    if k not in data:
        print(f"Missing seed key: {k}")
        sys.exit(1)

print("OK: seeds file present and contains required keys.")
