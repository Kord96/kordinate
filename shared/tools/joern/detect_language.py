#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROFILE_DIR = ROOT / "repo_profile"
sys.path.insert(0, str(PROFILE_DIR))

from repo_profile import detect_repo_profile  # type: ignore


def main() -> int:
    parser = argparse.ArgumentParser(description="Detect dominant repo language for Joern frontend selection.")
    parser.add_argument("repo_path", help="Absolute path to repository")
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of plain language")
    args = parser.parse_args()

    root = Path(args.repo_path)
    if not root.is_dir():
        raise SystemExit(f"repo path does not exist: {root}")

    profile = detect_repo_profile(root)
    if args.json:
        print(json.dumps(profile, indent=2, sort_keys=True))
    else:
        language = profile.get("dominant_language")
        if not language:
            raise SystemExit("unable to detect supported language")
        print(language)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
