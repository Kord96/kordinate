#!/usr/bin/env python3
"""Compatibility CLI for emitting only the frameworks fact domain."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from fact_extractor_support import build_facts_payload


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Detect framework context and emit the Augur frameworks fact domain.")
    parser.add_argument("root", nargs="?", default=".", help="Project root to scan.")
    parser.add_argument("--repo-dir", help="Alias for the project root to scan.")
    parser.add_argument("--project", help="Optional explicit project slug. Currently informational only.")
    parser.add_argument("--agent-home", help="Optional agent home directory. Accepted for path-contract compatibility.")
    parser.add_argument("--output", "-o", help="Write JSON to this file instead of stdout.")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    root_arg = args.repo_dir or args.root
    root = Path(root_arg).resolve()
    if not root.exists():
        print(f"error: root not found: {root}", file=sys.stderr)
        return 2
    if not root.is_dir():
        print(f"error: root is not a directory: {root}", file=sys.stderr)
        return 2

    payload = build_facts_payload(root, analysis_mode="full")
    frameworks = [fact for fact in payload.get("facts", []) if str(fact.get("domain") or "") == "frameworks"]
    domain_payload = {
        "version": payload.get("version", "1"),
        "generated": payload.get("generated"),
        "project": payload.get("project"),
        "analysis_mode": payload.get("analysis_mode"),
        "domain": "frameworks",
        "count": len(frameworks),
        "facts": frameworks,
    }
    serialized = json.dumps(domain_payload, indent=2 if args.pretty else None, sort_keys=bool(args.pretty))
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
