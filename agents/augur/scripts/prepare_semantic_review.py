#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PROMPT_PATH = ROOT / "skills" / "analyze" / "semantic-review-prompt.md"


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def build_fact_index(facts_payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {fact["id"]: fact for fact in facts_payload.get("facts", []) if fact.get("id")}


def packet_item(pattern: dict[str, Any], fact_index: dict[str, dict[str, Any]]) -> dict[str, Any]:
    verdict = pattern.get("verdict", {})
    fact_ids = verdict.get("fact_evidence", [])
    supporting_facts = []
    for fact_id in fact_ids[:12]:
        fact = fact_index.get(fact_id)
        if fact:
            supporting_facts.append(
                {
                    "id": fact_id,
                    "kind": fact.get("kind"),
                    "summary": fact.get("summary"),
                    "source_files": fact.get("source_files", []),
                    "raw_evidence": fact.get("raw_evidence", {}),
                }
            )
    return {
        "concept": pattern.get("id"),
        "category": pattern.get("category"),
        "confidence": pattern.get("confidence"),
        "components": pattern.get("components", []),
        "grounded_in": verdict.get("grounded_in", []),
        "fact_evidence": fact_ids,
        "detector_evidence": verdict.get("detector_evidence", []),
        "contradictions": verdict.get("contradictions", []),
        "review_required_reason": verdict.get("semantic_review", {}).get("review_required_reason", ""),
        "supporting_facts": supporting_facts,
    }


def build_review_packet(concepts_payload: dict[str, Any], facts_payload: dict[str, Any]) -> dict[str, Any]:
    fact_index = build_fact_index(facts_payload)
    candidates = []
    for pattern in concepts_payload.get("concepts", {}).get("detected_patterns", []):
        verdict = pattern.get("verdict", {})
        if not verdict.get("semantic_review", {}).get("required"):
            continue
        candidates.append(packet_item(pattern, fact_index))
    return {
        "version": "1",
        "prompt_path": str(PROMPT_PATH),
        "generated_from": {
            "concepts": concepts_payload.get("generated_from", ""),
            "facts": facts_payload.get("root", ""),
        },
        "candidates": candidates,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Prepare a semantic-review packet from inferred concepts and facts.")
    parser.add_argument("concepts_json", type=Path, help="Path to inferred concepts JSON.")
    parser.add_argument("facts_json", type=Path, help="Path to facts payload JSON.")
    parser.add_argument("--output", type=Path, required=True, help="Output review packet JSON path.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    concepts_payload = load_json(args.concepts_json)
    facts_payload = load_json(args.facts_json)
    write_json(args.output, build_review_packet(concepts_payload, facts_payload))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
