#!/usr/bin/env python3
"""Deterministic Augur fact extraction CLI."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from fact_extractor_support import build_facts_payload


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Extract normalized Augur facts from a project.")
    parser.add_argument("root", nargs="?", default=".", help="Project root to scan.")
    parser.add_argument("--output", "-o", help="Write JSON to this file instead of stdout.")
    parser.add_argument(
        "--analysis-mode",
        choices=["full", "incremental", "design"],
        default="full",
        help="Label the extraction run for downstream consumers.",
    )
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    root = Path(args.root).resolve()
    if not root.exists():
        print(f"error: root not found: {root}", file=sys.stderr)
        return 2
    if not root.is_dir():
        print(f"error: root is not a directory: {root}", file=sys.stderr)
        return 2

    payload = build_facts_payload(root, analysis_mode=args.analysis_mode)
    serialized = json.dumps(payload, indent=2 if args.pretty else None, sort_keys=bool(args.pretty))
    if args.pretty:
        serialized += "\n"

    if args.output:
        out = Path(args.output).resolve()
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(serialized, encoding="utf-8")
    else:
        sys.stdout.write(serialized)
        if not serialized.endswith("\n"):
            sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
