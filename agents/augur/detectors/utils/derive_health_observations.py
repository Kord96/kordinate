#!/usr/bin/env python3
"""Build normalized health observations from health candidate facts."""

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


def fact_payload(record: dict[str, Any]) -> dict[str, Any]:
    payload = record.get("fact")
    return payload if isinstance(payload, dict) else {}


def observation_kind(kind: str) -> str:
    if "integration" in kind:
        return "health"
    if "propagation" in kind:
        return "health"
    return "health"


def subject_for_payload(payload: dict[str, Any], kind: str) -> str:
    if "integration" in kind:
        source = str(payload.get("source") or "").strip()
        target = str(payload.get("target") or "").strip()
        if source and target:
            return f"{source}->{target}"
    if "propagation" in kind:
        source = str(payload.get("source") or "").strip()
        if source:
            return source
    component = str(payload.get("component") or "").strip()
    return component or str(payload.get("source") or "").strip() or "health-surface"


def next_actions(payload: dict[str, Any], kind: str) -> list[str]:
    actions: list[str] = []
    if "integration" in kind:
        actions.append("inspect the dependency boundary and caller behavior")
    elif "propagation" in kind:
        actions.append("inspect downstream degraded modes and containment paths")
    else:
        actions.append("inspect the local component health criteria and failure handling")
    for ref in payload.get("evidence_refs") or []:
        normalized = str(ref).strip()
        if normalized:
            actions.append(f"inspect {normalized}")
    return actions[:5]


def convert_record(record: dict[str, Any]) -> dict[str, Any]:
    payload = fact_payload(record)
    kind = str(payload.get("kind") or "").strip()
    return {
        "id": f"obs-{record.get('id')}",
        "kind": observation_kind(kind),
        "subject": subject_for_payload(payload, kind),
        "status": "candidate",
        "finding": str(record.get("summary") or payload.get("rationale") or ""),
        "confidence": str(payload.get("confidence_hint") or "medium"),
        "evidence": {
            "fact_ids": [str(record.get("id") or "")],
            "repo_refs": list(record.get("source_files") or []),
            "candidate_type": kind,
            "signals": list(payload.get("signals") or []),
            "affected_components": list(payload.get("affects") or []),
        },
        "counter_evidence": [],
        "gaps": list(payload.get("gaps") or []),
        "questions": [],
        "recommendation": "inspect_code",
        "next_actions": next_actions(payload, kind),
        "relationships": list(record.get("relationships") or []),
    }


def build_output(payload: dict[str, Any]) -> dict[str, Any]:
    observations = [convert_record(record) for record in (payload.get("facts") or []) if isinstance(record, dict)]
    return {
        "version": str(payload.get("version") or "1"),
        "generated": payload.get("generated"),
        "project": payload.get("project"),
        "analysis_mode": payload.get("analysis_mode"),
        "artifact": "health",
        "count": len(observations),
        "observations": observations,
        "metadata": {
            "source_fact_file": "facts/health-candidates.json",
            "selection_rules": list(payload.get("selection_rules") or []),
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Derive normalized health observations from facts/health-candidates.json")
    parser.add_argument("health_file", type=Path, help="Path to facts/health-candidates.json")
    parser.add_argument("--output", type=Path, required=True, help="Output observations JSON path")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    write_json(args.output, build_output(load_json(args.health_file)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
