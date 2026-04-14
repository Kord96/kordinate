#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PROJECTS_ROOT = Path("/kord/augur/memory/projects")
GLOBAL_ROOT = Path("/kord/augur/memory/global/reflections")


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def normalize_text(text: str) -> str:
    lowered = text.lower().strip()
    lowered = re.sub(r"\s+", " ", lowered)
    lowered = re.sub(r"[`\"'()\[\]{}]+", "", lowered)
    return lowered


def sentence_units(text: str) -> list[str]:
    stripped = text.strip()
    if not stripped:
        return []
    parts = re.split(r"(?<=[.!?])\s+|\n+", stripped)
    return [part.strip(" -") for part in parts if part.strip(" -")]


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def find_raw_reflections(root: Path) -> list[Path]:
    if root.is_file():
        return [root]
    return sorted(root.rglob("reflections/runs/*.json"))


def normalize_record(raw: dict[str, Any], raw_path: Path) -> dict[str, Any]:
    reflection = raw.get("reflection", {})
    project_text = reflection.get("project", "")
    general_text = reflection.get("general", "")
    signal_units = []

    for source_field, text in (("project", project_text), ("general", general_text)):
        for unit in sentence_units(text):
            signal_units.append({
                "source_field": source_field,
                "text": unit,
                "normalized_text": normalize_text(unit),
            })

    return {
        "reflection_id": raw["reflection_id"],
        "captured_at": raw.get("captured_at", ""),
        "repo": raw.get("repo", ""),
        "repo_url": raw.get("repo_url", ""),
        "pinned_sha": raw.get("pinned_sha", ""),
        "model": raw.get("model", ""),
        "provider": raw.get("provider", raw.get("backend_provider", "")),
        "runtime_kind": raw.get("runtime_kind", raw.get("backend_runtime", "")),
        "memory_bundle": raw.get("memory_bundle", ""),
        "skill_bundle": raw.get("skill_bundle", ""),
        "run_number": raw.get("run_number", 0),
        "analysis_mode": raw.get("analysis_mode", ""),
        "correlation_id": raw.get("correlation_id", ""),
        "reflection_prompt_path": raw.get("reflection_prompt_path", ""),
        "raw_reflection_path": str(raw_path),
        "reflection": {
            "project": project_text,
            "general": general_text,
        },
        "signal_units": signal_units,
    }


def build_manifest(records: list[dict[str, Any]]) -> dict[str, Any]:
    by_model: dict[str, int] = {}
    by_repo: dict[str, int] = {}
    for record in records:
        by_model[record.get("model", "unknown")] = by_model.get(record.get("model", "unknown"), 0) + 1
        by_repo[record.get("repo", "unknown")] = by_repo.get(record.get("repo", "unknown"), 0) + 1
    return {
        "generated_at": utc_now(),
        "record_count": len(records),
        "models": by_model,
        "repos": by_repo,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a normalized global reflection index from raw Augur reflection records.")
    parser.add_argument("--root", type=Path, default=PROJECTS_ROOT, help="Projects root or a single raw reflection file.")
    parser.add_argument("--output-root", type=Path, default=GLOBAL_ROOT / "records", help="Global reflection record root.")
    args = parser.parse_args()

    raw_files = find_raw_reflections(args.root)
    if not raw_files:
        raise SystemExit("No raw reflection records found.")

    normalized_records = []
    for raw_path in raw_files:
        raw = load_json(raw_path)
        normalized = normalize_record(raw, raw_path)
        normalized_records.append(normalized)
        write_json(args.output_root / f"{normalized['reflection_id']}.json", normalized)

    manifest_path = args.output_root.parent / "manifest.json"
    write_json(manifest_path, build_manifest(normalized_records))
    print(json.dumps({
        "output_root": str(args.output_root),
        "manifest_path": str(manifest_path),
        "record_count": len(normalized_records),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
