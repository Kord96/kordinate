#!/usr/bin/env python3
"""Export Augur-facing Joern fact payloads using one CPG build."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from common import DEFAULT_IMAGE_TAG, ROOT, detect_language, run_joern_queries
from export_call_edges import parse_rows as parse_call_edge_rows
from export_data_touches import parse_rows as parse_data_touch_rows
from export_execution_slices import parse_rows as parse_execution_slice_rows


CALL_EDGES_SCRIPT = ROOT / "queries" / "export_call_edges.sc"
DATA_TOUCHES_SCRIPT = ROOT / "queries" / "export_data_touches.sc"
EXECUTION_SLICES_SCRIPT = ROOT / "queries" / "export_execution_slices.sc"


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export Augur-facing Joern fact payloads from a repo using one CPG build.")
    parser.add_argument("repo", help="Absolute path to the repo root.")
    parser.add_argument("--language", help="Dominant repo language. Auto-detected when omitted.")
    parser.add_argument("--output", "-o", help="Write JSON to this file instead of stdout.")
    parser.add_argument("--image-tag", default=DEFAULT_IMAGE_TAG, help="Joern Docker image tag.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    repo = Path(args.repo).resolve()
    if not repo.exists():
        print(f"error: repo not found: {repo}", file=sys.stderr)
        return 2
    if not repo.is_dir():
        print(f"error: repo is not a directory: {repo}", file=sys.stderr)
        return 2
    if not repo.is_absolute():
        print(f"error: repo path must be absolute: {repo}", file=sys.stderr)
        return 2

    language = args.language or detect_language(repo)
    try:
        outputs = run_joern_queries(
            repo,
            language,
            [
                (CALL_EDGES_SCRIPT, "export_call_edges.sc"),
                (DATA_TOUCHES_SCRIPT, "export_data_touches.sc"),
                (EXECUTION_SLICES_SCRIPT, "export_execution_slices.sc"),
            ],
            args.image_tag,
        )
    except RuntimeError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    payload = {
        "version": "1",
        "tool": "joern",
        "language": language,
        "root": str(repo),
        "domains": {
            "call-edges": {
                "records": parse_call_edge_rows(outputs.get("export_call_edges.sc", "")),
            },
            "data-touches": {
                "records": parse_data_touch_rows(outputs.get("export_data_touches.sc", "")),
            },
            "execution-slices": {
                "records": parse_execution_slice_rows(outputs.get("export_execution_slices.sc", "")),
            },
        },
    }
    serialized = json.dumps(payload, indent=2) + "\n"
    if args.output:
        out = Path(args.output).resolve()
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(serialized, encoding="utf-8")
    else:
        sys.stdout.write(serialized)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
