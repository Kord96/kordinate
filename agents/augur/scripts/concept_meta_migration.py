#!/usr/bin/env python3
"""Generate and load Augur concept metadata.

This script supports the evidence-first concept metadata migration:
- builds `meta.yaml` files from legacy concept support files
- loads structured support, preferring `meta.yaml` and falling back to legacy files

The migration is additive and non-breaking: `concept.md` remains canonical and
legacy support files stay in place during rollout.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import yaml

from concept_loader import build_meta, load_structured_support, write_meta


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate and load Augur concept meta.yaml files")
    parser.add_argument("concept_dirs", nargs="+", help="Concept directories to process")
    parser.add_argument("--stdout", action="store_true", help="Print generated YAML to stdout instead of writing files")
    parser.add_argument("--load-json", action="store_true", help="Load structured support (meta.yaml first, legacy fallback) and print JSON")
    args = parser.parse_args()

    for raw_dir in args.concept_dirs:
        concept_dir = Path(raw_dir).resolve()
        if not concept_dir.is_dir():
            raise NotADirectoryError(concept_dir)

        if args.load_json:
            print(json.dumps(load_structured_support(concept_dir), indent=2))
            continue

        if args.stdout:
            payload = yaml.safe_dump(build_meta(concept_dir), sort_keys=False, allow_unicode=True, width=1000)
            print(f"# {concept_dir}")
            print(payload, end="")
        else:
            meta_path = write_meta(concept_dir)
            print(meta_path)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
