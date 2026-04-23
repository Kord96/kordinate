#!/usr/bin/env python3
"""Build normalized component observations from deterministic component seeds."""

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


def convert_seed(seed: dict[str, Any]) -> dict[str, Any]:
    representative = list(seed.get("representative_files") or [])
    actions: list[str] = []
    for key in ("entry_files", "flow_files", "state_or_ops_files"):
        for ref in seed.get(key) or []:
            normalized = str(ref).strip()
            if normalized:
                actions.append(f"inspect {normalized}")
    if not actions:
        actions = [f"inspect {ref}" for ref in representative[:3]]
    return {
        "id": f"obs-component-{seed.get('id')}",
        "kind": "architecture",
        "subject": str(seed.get("id") or seed.get("group") or ""),
        "status": "candidate",
        "finding": str(seed.get("rationale") or ""),
        "confidence": "medium" if int(seed.get("root_likelihood") or 0) >= 4 else "low",
        "evidence": {
            "fact_ids": [],
            "repo_refs": representative,
            "signals": list(seed.get("signals") or []),
            "group": str(seed.get("group") or ""),
            "root_likelihood": int(seed.get("root_likelihood") or 0),
        },
        "counter_evidence": [],
        "gaps": [],
        "questions": [],
        "recommendation": "inspect_code",
        "next_actions": actions[:5],
        "relationships": [],
    }


def build_output(payload: dict[str, Any]) -> dict[str, Any]:
    observations = [convert_seed(seed) for seed in (payload.get("candidate_components") or []) if isinstance(seed, dict)]
    return {
        "version": str(payload.get("version") or "1"),
        "generated": payload.get("generated"),
        "project": payload.get("project"),
        "analysis_mode": payload.get("analysis_mode"),
        "artifact": "components",
        "count": len(observations),
        "observations": observations,
        "metadata": {
            "source_derived_file": "derived/component-seeds.json",
            "planning_rules": list(payload.get("planning_rules") or []),
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Derive normalized component observations from derived/component-seeds.json")
    parser.add_argument("component_file", type=Path, help="Path to derived/component-seeds.json")
    parser.add_argument("--output", type=Path, required=True, help="Output observations JSON path")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    write_json(args.output, build_output(load_json(args.component_file)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
