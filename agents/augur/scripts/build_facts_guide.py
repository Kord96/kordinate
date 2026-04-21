#!/usr/bin/env python3
"""Build a run-specific interpretation guide for deterministic fact artifacts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT / "schemas" / "facts-catalog.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build Augur facts guide for one run")
    parser.add_argument("facts_dir", help="facts directory for the run")
    parser.add_argument("--output", required=True, help="Output JSON path")
    return parser.parse_args()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    args = parse_args()
    facts_dir = Path(args.facts_dir).resolve()
    output_path = Path(args.output).resolve()
    catalog = load_json(CATALOG_PATH)
    catalog_artifacts = catalog.get("artifacts", {}) or {}
    index_payload = load_json(facts_dir / "index.json") if (facts_dir / "index.json").exists() else {}
    startup_payload = load_json(facts_dir / "startup.json") if (facts_dir / "startup.json").exists() else {}

    startup_files = {
        str(item).removeprefix("facts/").removesuffix(".json")
        for item in (startup_payload.get("startup_files") or [])
        if isinstance(item, str)
    }

    startup_artifacts: list[dict[str, Any]] = [
        {
            "file": "facts/startup.json",
            "role": "Startup manifest for this run.",
        },
        {
            "file": "facts/facts-guide.json",
            "role": "Task-oriented retrieval policy for optional deterministic artifacts.",
        },
    ]
    for startup_file in startup_payload.get("startup_files") or []:
        if not isinstance(startup_file, str) or not startup_file.strip():
            continue
        normalized = startup_file.removeprefix("./")
        artifact_name = Path(normalized).stem
        catalog_entry = catalog_artifacts.get(artifact_name, {})
        startup_artifacts.append({
            "file": normalized,
            "role": catalog_entry.get("how_to_use", f"Use '{artifact_name}' for initial orientation only."),
        })

    targeted_domains = startup_payload.get("targeted_domains") or {}
    targeted_guidance: list[dict[str, Any]] = []
    group_meanings = {
        "concept_questions": "Reach for these only when concept validity, framework-shaped claims, or contradictions need resolution.",
        "decomposition_and_narratives": "Use these when component boundaries, story selection, or narrative teaching choices are the active problem.",
        "state_and_data_flow": "Use these when state ownership, flow truthfulness, or data movement is unclear.",
        "boundaries_and_dependencies": "Use these when boundary placement, handler ownership, auth surfaces, or external dependency modeling is unclear.",
        "health_and_failure": "Use these when health, monitoring, resilience, or failure-scenario coverage is the active problem.",
    }
    for group_name, files in targeted_domains.items():
        if not isinstance(files, list):
            continue
        existing = []
        for entry in files:
            if not isinstance(entry, str) or not entry.strip():
                continue
            normalized = entry.removeprefix("./")
            candidate = facts_dir.parent / normalized if normalized.startswith("facts/") else facts_dir / normalized
            if candidate.exists():
                existing.append(normalized)
        if existing:
            targeted_guidance.append({
                "name": group_name,
                "when": group_meanings.get(group_name, "Use these only when the current ambiguity specifically matches this area."),
                "files": existing,
            })

    payload = {
        "version": 1,
        "goal": "Run-specific interpretation guide for deterministic Augur fact artifacts.",
        "read_order": [
            "facts/startup.json",
            "facts/facts-guide.json",
        ],
        "rules": [
            "Read only the startup artifacts first, then move into repo code before consulting optional deterministic artifacts.",
            "Do not read facts/index.json during startup unless you genuinely need to discover an artifact not already covered by startup.json or this guide.",
            "Treat targeted deterministic artifacts as on-demand support for a specific ambiguity, validator finding, or review question.",
            "Deterministic artifacts are guidance and evidence, not final semantic conclusions.",
        ],
        "startup_artifacts": startup_artifacts,
        "targeted_guidance": targeted_guidance,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
