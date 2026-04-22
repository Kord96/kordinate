#!/usr/bin/env python3
"""Attach run-specific retrieval guidance to run-local index.json."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ARTIFACT_ROLES: dict[str, str] = {
    "frameworks": "Use to understand stack and framework-shaped boundaries before naming components.",
    "routes": "Use to identify request-facing surfaces, actors, and candidate flows.",
    "handlers": "Use to map transports and request or control entrypoints into code.",
    "dispatch-bindings": "Use to spot routing, queue, event, and runtime registration boundaries.",
    "boundaries": "Use to identify ports, adapters, repositories, service seams, and storage boundaries.",
    "external-clients": "Use to model external dependencies, resilience surfaces, and dependency boundaries.",
    "config": "Use to understand configuration flow, state sources, and mode variability.",
    "hot-files": "Use to prioritize early repo reads and breadth-pass candidates.",
    "call-edges": "Use to support dependency direction and boundary-crossing analysis.",
    "data-touches": "Use to enrich store readers and writers, state boundaries, and config reload paths.",
    "execution-slices": "Use to discover candidate flows and important execution paths.",
    "concepts": "Use to resolve concept candidates from supporting evidence, counter evidence, evidence gaps, review questions, and repo code.",
    "story-seeds": "Use to draft candidate child concerns before writing stories and narratives.",
    "component-seeds": "Use to choose representative entry, flow, and state or operations files for provisional top-level components.",
    "narrative-seeds": "Use to challenge which roots, child stories, and optional canonical narratives are actually justified for this repo.",
    "health-candidates": "Use to pressure health coverage and cascade reasoning before finalizing atlas health blocks.",
    "symbols-seed": "Use to prefer exact mechanism names from code when writing findings, summaries, and flow steps.",
    "state-seeds": "Use to tighten state claims around exact structs, enums, maps, config variants, and storage selectors.",
    "state-access-summary": "Use to identify state boundaries, likely ownership, and candidate child stories around storage.",
    "control-hotspots": "Use to prioritize breadth reads and candidate flow stories around chokepoints.",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Attach retrieval guidance to run-local index.json for one run")
    parser.add_argument("run_dir", help="run directory for the prepared analysis")
    parser.add_argument("--output", help="Deprecated explicit output path; defaults to <run>/index.json")
    return parser.parse_args()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    args = parse_args()
    run_dir = Path(args.run_dir).resolve()
    facts_dir = run_dir / "facts"
    derived_dir = run_dir / "derived"
    output_path = Path(args.output).resolve() if args.output else (run_dir / "index.json")
    index_payload = load_json(run_dir / "index.json") if (run_dir / "index.json").exists() else {}
    startup_payload = load_json(run_dir / "startup.json") if (run_dir / "startup.json").exists() else {}

    startup_artifacts: list[dict[str, Any]] = [
        {
            "file": "startup.json",
            "role": "Startup manifest for this run.",
        },
        {
            "file": "index.json",
            "role": "Canonical manifest plus retrieval policy for deterministic artifacts in this run.",
        },
    ]
    for startup_file in startup_payload.get("startup_files") or []:
        if not isinstance(startup_file, str) or not startup_file.strip():
            continue
        normalized = startup_file.removeprefix("./")
        artifact_name = Path(normalized).stem
        startup_artifacts.append({
            "file": normalized,
            "role": ARTIFACT_ROLES.get(artifact_name, f"Use '{artifact_name}' for initial orientation only."),
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
            candidate = run_dir / normalized
            if candidate.exists():
                existing.append(normalized)
        if existing:
            targeted_guidance.append({
                "name": group_name,
                "when": group_meanings.get(group_name, "Use these only when the current ambiguity specifically matches this area."),
                "files": existing,
            })

    guide_payload = {
        "version": 1,
        "goal": "Run-specific interpretation guide for deterministic Augur fact artifacts.",
        "read_order": [
            "startup.json",
            "index.json",
        ],
        "rules": [
            "Read only the startup artifacts first, then move into repo code before consulting optional deterministic artifacts.",
            "Use index.json when you genuinely need to discover an artifact not already covered by startup.json or to choose the right targeted support artifact.",
            "Treat targeted deterministic artifacts as on-demand support for a specific ambiguity, validator finding, or review question.",
            "Deterministic artifacts are guidance and evidence, not final semantic conclusions.",
        ],
        "startup_artifacts": startup_artifacts,
        "targeted_guidance": targeted_guidance,
    }
    index_payload["guide"] = guide_payload
    index_payload["facts_root"] = "facts/"
    index_payload["derived_root"] = "derived/"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(index_payload, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
