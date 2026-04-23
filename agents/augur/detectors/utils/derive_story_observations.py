#!/usr/bin/env python3
"""Build normalized story observations from deterministic story seeds."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def convert_concern(seed: dict[str, Any]) -> dict[str, Any]:
    concern = str(seed.get("class") or "").strip()
    evidence_domains = list(seed.get("evidence_domains") or [])
    return {
        "id": f"obs-story-{concern}",
        "kind": "story",
        "subject": concern,
        "status": "candidate",
        "finding": str(seed.get("why") or ""),
        "confidence": "medium",
        "evidence": {
            "fact_ids": [],
            "repo_refs": [],
            "evidence_domains": evidence_domains,
        },
        "counter_evidence": [],
        "gaps": [],
        "questions": [],
        "recommendation": "plan_story",
        "next_actions": [
            f"test whether `{concern}` deserves a dedicated story",
            f"use evidence from {', '.join(evidence_domains[:4])}" if evidence_domains else "inspect supporting repo slices",
        ],
        "relationships": [],
    }


def build_output(payload: dict[str, Any]) -> dict[str, Any]:
    observations = [convert_concern(seed) for seed in (payload.get("candidate_concern_classes") or []) if isinstance(seed, dict)]
    return {
        "version": str(payload.get("version") or "1"),
        "generated": payload.get("generated"),
        "project": payload.get("project"),
        "analysis_mode": payload.get("analysis_mode"),
        "artifact": "stories",
        "count": len(observations),
        "observations": observations,
        "metadata": {
            "source_derived_file": "derived/story-seeds.json",
            "planning_rules": list(payload.get("planning_rules") or []),
            "questions": list(payload.get("questions") or []),
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Derive normalized story observations from derived/story-seeds.json")
    parser.add_argument("story_file", type=Path, help="Path to derived/story-seeds.json")
    parser.add_argument("--output", type=Path, required=True, help="Output observations JSON path")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    write_json(args.output, build_output(load_json(args.story_file)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
