#!/usr/bin/env python3
"""Export normalized execution slice records from a repo using Joern."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from common import DEFAULT_IMAGE_TAG, ROOT, decode_field, detect_language, run_joern_query


QUERY_SCRIPT = ROOT / "queries" / "export_execution_slices.sc"
FIELDS = [
    "owner_name",
    "owner_full_name",
    "owner_file",
    "owner_line",
    "step_index",
    "callee_name",
    "callee_full_name",
    "call_code",
    "line_number",
    "column_number",
]


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export execution slices from a repo using Joern.")
    parser.add_argument("repo", help="Absolute path to the repo root.")
    parser.add_argument("--language", help="Dominant repo language. Auto-detected when omitted.")
    parser.add_argument("--output", "-o", help="Write JSON to this file instead of stdout.")
    parser.add_argument("--image-tag", default=DEFAULT_IMAGE_TAG, help="Joern Docker image tag.")
    return parser.parse_args(argv)


def parse_rows(stdout: str) -> list[dict[str, object]]:
    step_rows: list[dict[str, object]] = []
    for raw_line in stdout.splitlines():
        if not raw_line.strip():
            continue
        parts = raw_line.split("\t")
        if len(parts) != len(FIELDS):
            continue
        row: dict[str, object] = {}
        for key, value in zip(FIELDS, parts, strict=True):
            if key in {"owner_line", "step_index", "line_number", "column_number"}:
                try:
                    row[key] = int(value)
                except ValueError:
                    row[key] = -1
            else:
                row[key] = decode_field(value)
        step_rows.append(row)

    grouped: dict[tuple[str, str, int], dict[str, object]] = {}
    for row in step_rows:
        key = (str(row["owner_full_name"]), str(row["owner_file"]), int(row["owner_line"]))
        record = grouped.setdefault(
            key,
            {
                "slice_name": str(row["owner_name"]),
                "slice_full_name": str(row["owner_full_name"]),
                "slice_file": str(row["owner_file"]),
                "slice_line": int(row["owner_line"]),
                "steps": [],
            },
        )
        record["steps"].append(
            {
                "step_index": int(row["step_index"]),
                "callee_name": str(row["callee_name"]),
                "callee_full_name": str(row["callee_full_name"]),
                "call_code": str(row["call_code"]),
                "line_number": int(row["line_number"]),
                "column_number": int(row["column_number"]),
            }
        )
    for record in grouped.values():
        record["steps"] = sorted(record["steps"], key=lambda item: (item["step_index"], item["line_number"], item["column_number"]))
    return list(grouped.values())


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
        stdout = run_joern_query(repo, language, QUERY_SCRIPT, "export_execution_slices.sc", args.image_tag)
    except RuntimeError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    payload = {
        "version": "1",
        "tool": "joern",
        "language": language,
        "root": str(repo),
        "records": parse_rows(stdout),
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
