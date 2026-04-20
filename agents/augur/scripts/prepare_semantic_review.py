#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PROMPT_PATH = ROOT / "skills" / "analyze" / "audit" / "prompts" / "semantic-review.md"


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def build_fact_index(facts_payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {fact["id"]: fact for fact in facts_payload.get("facts", []) if fact.get("id")}


def framework_review_context(concept_evidence_payload: dict[str, Any]) -> dict[str, Any]:
    metadata = concept_evidence_payload.get("metadata", {})
    context = metadata.get("framework_review_context") if isinstance(metadata, dict) else {}
    if not isinstance(context, dict):
        return {
            "detected_frameworks": [],
            "inspect_concepts": [],
            "focus_areas": [],
            "concept_to_frameworks": {},
        }
    return {
        "detected_frameworks": list(context.get("detected_frameworks") or []),
        "inspect_concepts": list(context.get("inspect_concepts") or []),
        "focus_areas": list(context.get("focus_areas") or []),
        "concept_to_frameworks": dict(context.get("concept_to_frameworks") or {}),
    }


def packet_item(fact: dict[str, Any], fact_index: dict[str, dict[str, Any]]) -> dict[str, Any]:
    raw_evidence = fact.get("raw_evidence", {})
    relationships = fact.get("relationships", {})
    evidence = fact.get("evidence") or {}
    supporting = evidence.get("supporting") or {}
    review = fact.get("review") or {}
    questions = review.get("questions") or {}
    fact_ids = list(supporting.get("fact_ids") or [])
    supporting_facts = []
    for fact_id in fact_ids[:12]:
        supporting_fact = fact_index.get(fact_id)
        if supporting_fact:
            supporting_facts.append(
                {
                    "id": fact_id,
                    "kind": supporting_fact.get("kind"),
                    "summary": supporting_fact.get("summary"),
                    "source_files": supporting_fact.get("source_files", []),
                    "raw_evidence": supporting_fact.get("raw_evidence", {}),
                }
            )
    return {
        "concept": raw_evidence.get("concept_id"),
        "category": raw_evidence.get("category"),
        "confidence": fact.get("confidence"),
        "components": relationships.get("component_ids", []),
        "grounded_in": relationships.get("component_ids", []),
        "fact_evidence": fact_ids,
        "detector_evidence": [fact.get("detector", {})] if fact.get("detector") else [],
        "counter_evidence": evidence.get("counter", []),
        "evidence_gaps": evidence.get("gaps", []),
        "review_required_reason": (
            "Deterministic concept evidence requires semantic adjudication."
            if review.get("required")
            else ""
        ),
        "review_questions": questions,
        "framework_hints": raw_evidence.get("framework_heuristics", {}),
        "supporting_facts": supporting_facts,
    }


def build_review_packet(concept_evidence_payload: dict[str, Any], facts_payload: dict[str, Any]) -> dict[str, Any]:
    fact_index = build_fact_index(facts_payload)
    review_context = framework_review_context(concept_evidence_payload)
    candidates = []
    for fact in concept_evidence_payload.get("facts", []):
        raw_evidence = fact.get("raw_evidence", {})
        if fact.get("kind") != "concept-candidate":
            continue
        if not (fact.get("review") or {}).get("required"):
            continue
        candidates.append(packet_item(fact, fact_index))
    return {
        "version": "1",
        "prompt_path": str(PROMPT_PATH),
        "generated_from": {
            "concept_evidence": concept_evidence_payload.get("metadata", {}).get("generated_from", ""),
            "facts": facts_payload.get("root", ""),
        },
        "framework_review_context": review_context,
        "candidates": candidates,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Prepare a semantic-review packet from concept evidence facts and facts.")
    parser.add_argument("concept_evidence_json", type=Path, help="Path to deterministic concept-evidence JSON.")
    parser.add_argument("facts_json", type=Path, help="Path to facts payload JSON.")
    parser.add_argument("--output", type=Path, required=True, help="Output review packet JSON path.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    concept_evidence_payload = load_json(args.concept_evidence_json)
    facts_payload = load_json(args.facts_json)
    write_json(args.output, build_review_packet(concept_evidence_payload, facts_payload))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
