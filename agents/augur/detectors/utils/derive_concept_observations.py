#!/usr/bin/env python3
"""Build normalized concept observations from deterministic concept facts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from layout import find_reference_file, load_markdown_frontmatter


ROOT = Path(__file__).resolve().parents[2]
MEMORY_CONCEPTS = ROOT / "memory" / "concepts"


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def fact_payload(record: dict[str, Any]) -> dict[str, Any]:
    payload = record.get("fact")
    return payload if isinstance(payload, dict) else {}


def read_concept_frontmatter(concept_id: str) -> tuple[str | None, dict[str, Any]]:
    reference = find_reference_file(MEMORY_CONCEPTS, concept_id)
    if reference is None:
        return None, {}
    try:
        return str(reference.relative_to(ROOT)), load_markdown_frontmatter(reference)
    except Exception:
        return str(reference), {}


def signature_summary(frontmatter: dict[str, Any]) -> dict[str, Any]:
    signatures = frontmatter.get("signatures") if isinstance(frontmatter.get("signatures"), dict) else {}
    if not signatures:
        return {}
    positive = signatures.get("positive") if isinstance(signatures.get("positive"), dict) else {}
    return {
        "positive": {
            key: list(values)[:4]
            for key, values in positive.items()
            if isinstance(values, list) and values
        },
        "negative": list(signatures.get("negative") or [])[:6],
        "notes": list(signatures.get("notes") or [])[:4],
    }


def semantic_summary(frontmatter: dict[str, Any]) -> dict[str, Any]:
    summary: dict[str, Any] = {}
    if frontmatter.get("name"):
        summary["name"] = str(frontmatter.get("name"))
    if isinstance(frontmatter.get("abstraction"), list) and frontmatter.get("abstraction"):
        summary["abstraction"] = list(frontmatter.get("abstraction"))
    if frontmatter.get("type"):
        summary["type"] = str(frontmatter.get("type"))
    if isinstance(frontmatter.get("relationships"), dict) and frontmatter.get("relationships"):
        relationships: dict[str, list[str]] = {}
        for key in ("implements", "supports", "related_to", "uses"):
            values = frontmatter.get("relationships", {}).get(key)
            if isinstance(values, list) and values:
                relationships[key] = list(values)
        if relationships:
            summary["relationships"] = relationships
    return summary


def next_actions(payload: dict[str, Any]) -> list[str]:
    actions: list[str] = []
    review = payload.get("review") if isinstance(payload.get("review"), dict) else {}
    questions = review.get("questions") if isinstance(review.get("questions"), dict) else {}
    if questions.get("entries"):
        actions.append("answer concept review questions before accepting the candidate")
    framework_heuristics = payload.get("framework_heuristics") if isinstance(payload.get("framework_heuristics"), dict) else {}
    for item in framework_heuristics.get("focus_areas") or []:
        normalized = str(item).strip()
        if normalized:
            actions.append(normalized)
    for item in payload.get("evidence_gaps") or []:
        normalized = str(item).strip()
        if normalized:
            actions.append(f"resolve evidence gap: {normalized}")
    detector_backing = str(payload.get("detector_backing") or "").strip()
    if detector_backing in {"weak", "partial"}:
        actions.append("inspect supporting repo code before promoting this concept")
    return actions[:6]


def observation_status(payload: dict[str, Any]) -> str:
    review = payload.get("review") if isinstance(payload.get("review"), dict) else {}
    if review.get("required"):
        return "needs-review"
    detector_backing = str(payload.get("detector_backing") or "").strip()
    if detector_backing == "strong":
        return "supported"
    return "candidate"


def convert_record(record: dict[str, Any]) -> dict[str, Any] | None:
    payload = fact_payload(record)
    if str(payload.get("kind") or "") != "concept-candidate":
        return None
    concept_id = str(payload.get("concept_id") or "").strip()
    if not concept_id:
        return None
    doc_path, frontmatter = read_concept_frontmatter(concept_id)
    evidence_summary = payload.get("evidence_summary") if isinstance(payload.get("evidence_summary"), dict) else {}
    review = payload.get("review") if isinstance(payload.get("review"), dict) else {}
    questions = review.get("questions") if isinstance(review.get("questions"), dict) else {}
    framework_heuristics = payload.get("framework_heuristics") if isinstance(payload.get("framework_heuristics"), dict) else {}

    return {
        "id": f"obs-{record.get('id')}",
        "kind": "concept",
        "subject": concept_id,
        "status": observation_status(payload),
        "finding": str(record.get("summary") or f"Deterministic evidence suggests concept `{concept_id}`."),
        "confidence": str(payload.get("confidence_hint") or "low"),
        "evidence": {
            "fact_ids": list(evidence_summary.get("fact_ids") or []),
            "repo_refs": list(record.get("source_files") or []),
            "doc_refs": [doc_path] if doc_path else [],
            "detector_backing": str(payload.get("detector_backing") or ""),
            "semantic_signatures": signature_summary(frontmatter),
            "semantic_summary": semantic_summary(frontmatter),
            "framework_context": {
                "suggested_by_frameworks": list(framework_heuristics.get("suggested_by_frameworks") or []),
                "inspect_next": list(framework_heuristics.get("inspect_next") or []),
            },
        },
        "counter_evidence": list(payload.get("counter_evidence") or evidence_summary.get("counter") or []),
        "gaps": list(payload.get("evidence_gaps") or evidence_summary.get("gaps") or []),
        "questions": [
            {
                "id": str(entry.get("id") or "").strip(),
                "prompt": str(entry.get("prompt") or "").strip(),
                "weight": entry.get("weight"),
                "signals": list(entry.get("signals") or []),
            }
            for entry in (questions.get("entries") or [])
            if isinstance(entry, dict) and str(entry.get("prompt") or "").strip()
        ],
        "recommendation": str(questions.get("recommended_next_step") or "inspect_code"),
        "next_actions": next_actions(payload),
        "relationships": list(record.get("relationships") or []),
    }


def build_output(concepts_payload: dict[str, Any]) -> dict[str, Any]:
    observations = [
        converted
        for converted in (convert_record(record) for record in (concepts_payload.get("facts") or []))
        if converted is not None
    ]
    return {
        "version": str(concepts_payload.get("version") or "1"),
        "generated": concepts_payload.get("generated"),
        "project": concepts_payload.get("project"),
        "analysis_mode": concepts_payload.get("analysis_mode"),
        "artifact": "concepts",
        "count": len(observations),
        "observations": observations,
        "metadata": {
            "source_fact_file": "facts/concepts.json",
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Derive normalized concept observations from facts/concepts.json")
    parser.add_argument("concepts_file", type=Path, help="Path to facts/concepts.json")
    parser.add_argument("--output", type=Path, required=True, help="Output observations JSON path")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = load_json(args.concepts_file)
    write_json(args.output, build_output(payload))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
