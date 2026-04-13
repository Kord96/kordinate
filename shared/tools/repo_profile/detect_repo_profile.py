#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from repo_profile import detect_repo_profile


def main() -> int:
    parser = argparse.ArgumentParser(description="Detect deterministic repo profile metadata.")
    parser.add_argument("repo_path", help="Absolute path to repository")
    parser.add_argument("--json", action="store_true", help="Emit JSON")
    parser.add_argument("--field", choices=["dominant_language"], help="Emit a single field")
    args = parser.parse_args()

    root = Path(args.repo_path)
    if not root.is_dir():
      raise SystemExit(f"repo path does not exist: {root}")

    profile = detect_repo_profile(root)
    if args.field:
        value = profile.get(args.field)
        if value is None:
            raise SystemExit(f"field unavailable: {args.field}")
        print(value)
        return 0
    if args.json or True:
        print(json.dumps(profile, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
