#!/usr/bin/env python3
"""Derive deterministic shared failure-scenario candidates from prepared fact artifacts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Derive Augur failure-scenario candidates from deterministic facts")
    parser.add_argument("facts_dir", help="facts/ directory for the prepared run")
    parser.add_argument("--output", required=True, help="Output JSON path")
    return parser.parse_args()


def unique_strings(values: list[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for value in values:
        value = str(value or "").strip()
        if not value or value in seen:
            continue
        seen.add(value)
        ordered.append(value)
    return ordered


def stable_id(*parts: str) -> str:
    normalized = "-".join(
        "".join(ch.lower() if ch.isalnum() else "-" for ch in str(part).strip()).strip("-")
        for part in parts
        if str(part).strip()
    )
    while "--" in normalized:
        normalized = normalized.replace("--", "-")
    return normalized[:96] or "candidate"


def load_optional_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = load_json(path)
    except Exception:
        return {}
    return payload if isinstance(payload, dict) else {}


def concept_monitoring_index() -> dict[str, dict[str, Any]]:
    for path in (
        ROOT / ".generated" / "bundles" / "detectors" / "concept-evidence" / "monitoring.json",
        ROOT / "bundles" / "detectors" / "concept-evidence" / "monitoring.json",
    ):
        if not path.exists():
            continue
        try:
            payload = load_json(path)
        except Exception:
            continue
        concepts = payload.get("concepts")
        if isinstance(concepts, dict):
            return {str(key): value for key, value in concepts.items() if isinstance(value, dict)}
    return {}


def strong_concept_candidates(concept_payload: dict[str, Any]) -> list[dict[str, Any]]:
    selected: list[dict[str, Any]] = []
    for fact in concept_payload.get("facts") or []:
        if not isinstance(fact, dict) or fact.get("kind") != "concept-candidate":
            continue
        raw = fact.get("raw_evidence") or {}
        detector_backing = str(raw.get("detector_backing") or "weak").strip().lower()
        confidence = str(fact.get("confidence") or "low").strip().lower()
        semantic_review_required = bool(raw.get("semantic_review_required"))
        if detector_backing == "weak":
            continue
        if semantic_review_required and not (detector_backing == "strong" and confidence == "high"):
            continue
        if detector_backing == "partial" and confidence != "high":
            continue
        selected.append(fact)
    return selected


def build_candidates(
    health_candidates_payload: dict[str, Any],
    concept_payload: dict[str, Any],
    monitoring_index: dict[str, dict[str, Any]],
    component_seed_ids: set[str],
) -> list[dict[str, Any]]:
    candidates: dict[str, dict[str, Any]] = {}

    def ensure(candidate_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        existing = candidates.get(candidate_id)
        if existing:
            return existing
        candidates[candidate_id] = payload
        return payload

    for candidate in health_candidates_payload.get("propagation_candidates") or []:
        if not isinstance(candidate, dict):
            continue
        source = str(candidate.get("source") or "").strip()
        affects = [str(item) for item in (candidate.get("affects") or []) if str(item or "").strip()]
        if not source or not affects:
            continue
        candidate_id = str(candidate.get("id") or stable_id(source, "shared-cascade"))
        starts_at = [source]
        chain = [
            {
                "from": source,
                "to": target,
                "effect": str(candidate.get("degraded_mode_hint") or "Dependent behavior degrades or stalls.").strip(),
            }
            for target in affects
        ]
        ensure(
            candidate_id,
            {
                "id": candidate_id,
                "scope": "cascading",
                "starts_at": starts_at,
                "involves": unique_strings(starts_at + affects),
                "chain": chain,
                "degraded_mode_hint": str(candidate.get("degraded_mode_hint") or ""),
                "containment_hint": str(candidate.get("containment_hint") or ""),
                "signal_hints": [],
                "mitigation_hints": [],
                "gaps": [],
                "concept_sources": [],
                "evidence_refs": unique_strings([str(ref) for ref in (candidate.get("evidence_refs") or []) if ref])[:4],
                "rationale": str(candidate.get("rationale") or ""),
            },
        )

    for fact in strong_concept_candidates(concept_payload):
        raw = fact.get("raw_evidence") or {}
        concept_id = str(raw.get("concept_id") or "").strip()
        monitoring = monitoring_index.get(concept_id)
        if not monitoring:
            continue
        components = [
            str(item)
            for item in ((fact.get("relationships") or {}).get("component_ids") or [])
            if str(item or "").strip() and str(item or "").strip() in component_seed_ids
        ]
        if len(set(components)) < 2:
            continue
        candidate_id = stable_id(concept_id, "concept-cascade")
        entry = ensure(
            candidate_id,
            {
                "id": candidate_id,
                "scope": "cascading",
                "starts_at": unique_strings(components[:2]),
                "involves": unique_strings(components),
                "chain": [],
                "degraded_mode_hint": f"Shared {concept_id} behavior can degrade multiple architecture slices together.",
                "containment_hint": "State whether retries, stale reads, cached results, or partial functionality contain the blast radius.",
                "signal_hints": [],
                "mitigation_hints": [],
                "gaps": [],
                "concept_sources": [],
                "evidence_refs": unique_strings([str(ref) for ref in (fact.get('source_files') or []) if ref])[:4],
                "rationale": f"Strong concept evidence plus monitoring expectations suggest a shared failure scenario around `{concept_id}`.",
            },
        )
        entry["concept_sources"] = unique_strings(list(entry.get("concept_sources") or []) + [concept_id])
        entry["signal_hints"] = unique_strings(
            list(entry.get("signal_hints") or [])
            + [str(item.get("name") or "") for item in (monitoring.get("health_signals") or []) if isinstance(item, dict) and item.get("name")]
        )
        entry["gaps"] = unique_strings(list(entry.get("gaps") or []) + [str(item) for item in (monitoring.get("gaps") or []) if item])
        if not entry["chain"]:
            root = entry["starts_at"][0] if entry["starts_at"] else components[0]
            entry["chain"] = [{"from": root, "to": target, "effect": entry["degraded_mode_hint"]} for target in components if target != root]

    ranked = sorted(
        candidates.values(),
        key=lambda item: (-len(item.get("involves") or []), -len(item.get("evidence_refs") or []), str(item.get("id") or "")),
    )
    for item in ranked:
        item["starts_at"] = unique_strings(list(item.get("starts_at") or []))
        item["involves"] = unique_strings(list(item.get("involves") or []))
        item["signal_hints"] = unique_strings(list(item.get("signal_hints") or []))
        item["mitigation_hints"] = unique_strings(list(item.get("mitigation_hints") or []))
        item["gaps"] = unique_strings(list(item.get("gaps") or []))
        item["concept_sources"] = unique_strings(list(item.get("concept_sources") or []))
    return ranked


def main() -> int:
    args = parse_args()
    facts_dir = Path(args.facts_dir).resolve()
    output_path = Path(args.output).resolve()
    health_candidates_payload = load_optional_json(facts_dir / "health-candidates.json")
    concept_payload = load_optional_json(facts_dir / "concept-evidence.json")
    monitoring_index = concept_monitoring_index()
    component_seeds_payload = load_optional_json(facts_dir / "component-seeds.json")
    component_seed_ids = {
        str(item.get("id") or "")
        for item in (component_seeds_payload.get("candidate_components") or [])
        if isinstance(item, dict) and str(item.get("id") or "").strip()
    }

    payload = {
        "version": 1,
        "goal": "Advisory shared failure-scenario candidates derived from deterministic facts and strong concept monitoring expectations.",
        "candidates": build_candidates(health_candidates_payload, concept_payload, monitoring_index, component_seed_ids),
        "selection_rules": [
            "Use these candidates for cross-unit failure chains, not for purely local failures.",
            "Prefer a shared failure_scenario when the same cascade would otherwise be repeated across several unit descriptions.",
            "Keep unit health focused on criteria plus shared-scenario links even when a shared failure scenario exists.",
        ],
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
