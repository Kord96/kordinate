#!/usr/bin/env python3
"""Derive deterministic story-planning seeds from prepared fact artifacts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Derive Augur story seeds from deterministic facts")
    parser.add_argument("facts_dir", help="facts/ directory for the prepared run")
    parser.add_argument("--output", required=True, help="Output JSON path")
    return parser.parse_args()


def existing_domain_names(index_payload: dict[str, Any]) -> set[str]:
    names: set[str] = set()
    for domain in (index_payload.get("index", {}) or {}).get("domains", []) or []:
        name = str((domain or {}).get("name") or "").strip()
        if name:
            names.add(name)
    return names


def concern_seeds_for_domains(domains: set[str]) -> list[dict[str, Any]]:
    seeds: list[dict[str, Any]] = [
        {
            "class": "composition-root",
            "why": "Every full run should identify startup wiring and ownership boundaries before writing stories.",
            "evidence_domains": sorted(domains & {"frameworks", "boundaries", "dispatch-bindings", "hot-files"}),
        }
    ]
    if domains & {"routes", "handlers", "dispatch-bindings", "external-clients"}:
        seeds.append({
            "class": "request-or-control-flow",
            "why": "A major request, control, or translation path usually deserves a child story.",
            "evidence_domains": sorted(domains & {"routes", "handlers", "dispatch-bindings", "external-clients"}),
        })
    if domains & {"storage", "config", "models", "schemas"}:
        seeds.append({
            "class": "state-boundary",
            "why": "Important stores, config sources, or schema boundaries often deserve their own child story.",
            "evidence_domains": sorted(domains & {"storage", "config", "models", "schemas"}),
        })
    if domains & {"jobs", "workers", "events", "messaging"}:
        seeds.append({
            "class": "background-or-event-path",
            "why": "Background pipelines and event-driven behavior often need separate explanation from synchronous request paths.",
            "evidence_domains": sorted(domains & {"jobs", "workers", "events", "messaging"}),
        })
    if domains & {"external-clients", "auth", "security", "observability"}:
        seeds.append({
            "class": "dependency-or-operations-boundary",
            "why": "External dependency handling, security, or operations surfaces often carry real failure and ownership boundaries.",
            "evidence_domains": sorted(domains & {"external-clients", "auth", "security", "observability"}),
        })
    return seeds


def main() -> int:
    args = parse_args()
    facts_dir = Path(args.facts_dir).resolve()
    output_path = Path(args.output).resolve()
    run_dir = facts_dir.parent

    index_payload = load_json(run_dir / "index.json") if (run_dir / "index.json").exists() else {}
    startup_payload = load_json(run_dir / "startup.json") if (run_dir / "startup.json").exists() else {}
    hot_files_payload = load_json(facts_dir / "hot-files.json") if (facts_dir / "hot-files.json").exists() else {}

    domains = existing_domain_names(index_payload)
    startup_files = startup_payload.get("startup_files") or []
    hot_files = hot_files_payload.get("facts") or hot_files_payload.get("hot_files") or []

    payload = {
        "version": 1,
        "goal": "Advisory seeds for story planning and child-story decomposition.",
        "planning_rules": [
            "Use these seeds to draft 2-3 candidate child concerns per root story before writing outputs.",
            "Prefer concern classes grounded in real flows, state boundaries, dependency boundaries, or operational failure paths.",
            "Merge weak restatements back into the parent story rather than creating decorative children.",
        ],
        "recommended_root_story_child_budget": {
            "default_min": 2,
            "default_target": 2,
            "default_max": 3,
        },
        "candidate_concern_classes": concern_seeds_for_domains(domains),
        "starter_files": startup_files[:12],
        "hot_files": hot_files[:12],
        "questions": [
            "Which distinct concern types exist under each provisional top-level component: composition, flow, state, dependency, or operations?",
            "Which root stories currently hide multiple real concerns that should be split into child stories?",
            "Which narrative should use a child story instead of repeating only root stories?",
        ],
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
