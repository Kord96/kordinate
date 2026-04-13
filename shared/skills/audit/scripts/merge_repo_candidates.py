#!/usr/bin/env python3
"""Merge first-pass repo candidate files from multiple models.

Usage:
  python3 shared/skills/audit/scripts/merge_repo_candidates.py \
    shared/skills/audit/references/repo-candidates/*.json \
    --output /tmp/repo-candidates-merged.json
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("inputs", nargs="+", help="Candidate JSON files to merge")
    parser.add_argument("--output", required=True, help="Where to write merged JSON")
    return parser.parse_args()


def normalize_repo(value: str) -> str:
    text = value.strip()
    text = re.sub(r"^https?://github\.com/", "", text, flags=re.IGNORECASE)
    text = text.strip("/")
    return text


def ensure_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(v).strip() for v in value if str(v).strip()]
    text = str(value).strip()
    return [text] if text else []


def merge_text(existing: str, incoming: str) -> str:
    existing = (existing or "").strip()
    incoming = (incoming or "").strip()
    if not existing:
        return incoming
    if not incoming or incoming == existing:
        return existing
    return f"{existing}\n\n---\n\n{incoming}"


def main() -> int:
    args = parse_args()
    merged: dict[str, dict[str, Any]] = {}

    for input_name in args.inputs:
        path = Path(input_name)
        data = json.loads(path.read_text())
        if not isinstance(data, list):
            raise ValueError(f"{path} does not contain a JSON array")

        for item in data:
            repo = normalize_repo(item["repo"])
            url = item.get("url") or f"https://github.com/{repo}"
            existing = merged.get(repo)
            if existing is None:
                merged[repo] = {
                    "repo": repo,
                    "url": url,
                    "suggested_by": sorted(set(ensure_list(item.get("suggested_by")))),
                    "reason_for_inclusion": (item.get("reason_for_inclusion") or "").strip(),
                    "what_it_tests": (item.get("what_it_tests") or "").strip(),
                    "risks_or_caveats": (item.get("risks_or_caveats") or "").strip(),
                    "source_files": [str(path)],
                }
                continue

            existing["suggested_by"] = sorted(
                set(existing["suggested_by"]) | set(ensure_list(item.get("suggested_by")))
            )
            existing["reason_for_inclusion"] = merge_text(
                existing["reason_for_inclusion"], item.get("reason_for_inclusion", "")
            )
            existing["what_it_tests"] = merge_text(
                existing["what_it_tests"], item.get("what_it_tests", "")
            )
            existing["risks_or_caveats"] = merge_text(
                existing["risks_or_caveats"], item.get("risks_or_caveats", "")
            )
            if str(path) not in existing["source_files"]:
                existing["source_files"].append(str(path))

    output = [merged[key] for key in sorted(merged)]
    Path(args.output).write_text(json.dumps(output, indent=2) + "\n")
    print(f"Merged {len(args.inputs)} files into {len(output)} unique repos -> {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
