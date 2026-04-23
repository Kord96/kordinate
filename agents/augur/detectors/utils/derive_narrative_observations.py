#!/usr/bin/env python3
"""Build normalized narrative observations from deterministic narrative seeds."""

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


def convert_narrative(item: dict[str, Any]) -> dict[str, Any]:
    evidence = item.get("evidence") if isinstance(item.get("evidence"), dict) else {}
    return {
        "id": f"obs-narrative-{item.get('id')}",
        "kind": "narrative",
        "subject": str(item.get("id") or ""),
        "status": "candidate",
        "finding": str(item.get("reason") or ""),
        "confidence": "high" if bool(item.get("required")) else "medium",
        "evidence": {
            "fact_ids": [],
            "repo_refs": [],
            "score": int(item.get("score") or 0),
            "evidence": evidence,
        },
        "counter_evidence": [],
        "gaps": [],
        "questions": [],
        "recommendation": "plan_narrative",
        "next_actions": [
            f"test whether `{item.get('id')}` earns a narrative slot",
            "verify the teaching path against story and component observations",
        ],
        "relationships": [],
    }


def build_output(payload: dict[str, Any]) -> dict[str, Any]:
    observations = [convert_narrative(item) for item in (payload.get("recommended_narratives") or []) if isinstance(item, dict)]
    return {
        "version": str(payload.get("version") or "1"),
        "generated": payload.get("generated"),
        "project": payload.get("project"),
        "analysis_mode": payload.get("analysis_mode"),
        "artifact": "narratives",
        "count": len(observations),
        "observations": observations,
        "metadata": {
            "source_derived_file": "derived/narrative-seeds.json",
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Derive normalized narrative observations from derived/narrative-seeds.json")
    parser.add_argument("narrative_file", type=Path, help="Path to derived/narrative-seeds.json")
    parser.add_argument("--output", type=Path, required=True, help="Output observations JSON path")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    write_json(args.output, build_output(load_json(args.narrative_file)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
