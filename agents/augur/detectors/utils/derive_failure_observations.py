#!/usr/bin/env python3
"""Build normalized failure observations from failure scenario candidate facts."""

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


def convert_record(record: dict[str, Any]) -> dict[str, Any]:
    payload = fact_payload(record)
    involves = list(payload.get("involves") or [])
    starts = list(payload.get("starts_at") or [])
    subject = ",".join(starts[:2] or involves[:2] or ["failure-scenario"])
    return {
        "id": f"obs-{record.get('id')}",
        "kind": "failure",
        "subject": subject,
        "status": "candidate",
        "finding": str(record.get("summary") or payload.get("rationale") or ""),
        "confidence": str(payload.get("confidence_hint") or "medium"),
        "evidence": {
            "fact_ids": [str(record.get("id") or "")],
            "repo_refs": list(record.get("source_files") or []),
            "starts_at": starts,
            "involves": involves,
            "signal_hints": list(payload.get("signal_hints") or []),
            "mitigation_hints": list(payload.get("mitigation_hints") or []),
        },
        "counter_evidence": [],
        "gaps": list(payload.get("gaps") or []),
        "questions": [],
        "recommendation": "inspect_code",
        "next_actions": [
            "inspect the start of the failure chain",
            *[f"inspect {ref}" for ref in list(record.get("source_files") or [])[:4]],
        ][:5],
        "relationships": list(record.get("relationships") or []),
    }


def build_output(payload: dict[str, Any]) -> dict[str, Any]:
    observations = [convert_record(record) for record in (payload.get("facts") or []) if isinstance(record, dict)]
    return {
        "version": str(payload.get("version") or "1"),
        "generated": payload.get("generated"),
        "project": payload.get("project"),
        "analysis_mode": payload.get("analysis_mode"),
        "artifact": "failure-scenarios",
        "count": len(observations),
        "observations": observations,
        "metadata": {
            "source_fact_file": "facts/failure-scenario-candidates.json",
            "selection_rules": list(payload.get("selection_rules") or []),
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Derive normalized failure observations from facts/failure-scenario-candidates.json")
    parser.add_argument("failure_file", type=Path, help="Path to facts/failure-scenario-candidates.json")
    parser.add_argument("--output", type=Path, required=True, help="Output observations JSON path")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    write_json(args.output, build_output(load_json(args.failure_file)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
