#!/usr/bin/env python3
"""Infer Augur concepts from normalized facts.

This script is intentionally pragmatic rather than exhaustive. It turns the new
facts layer into atlas-compatible concept evidence so Augur can move toward a
facts-first pipeline without waiting on every concept detector to be rewritten.
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def iter_fact_files(facts_dir: Path) -> list[Path]:
    index_file = facts_dir / "index.json"
    if index_file.exists():
        index = load_json(index_file)
        files = []
        for domain in index.get("index", {}).get("domains", []):
            rel = domain.get("file")
            if rel:
                files.append((facts_dir.parent / rel).resolve())
        return [path for path in files if path.exists()]
    return sorted(p for p in facts_dir.glob("*.json") if p.name != "index.json")


def load_facts(facts_dir: Path) -> list[dict[str, Any]]:
    facts: list[dict[str, Any]] = []
    for path in iter_fact_files(facts_dir):
        payload = load_json(path)
        if isinstance(payload, dict) and "facts" in payload:
            facts.extend(payload["facts"])
        elif isinstance(payload, list):
            facts.extend(payload)
    return facts


def confidence_from_count(count: int) -> str:
    if count >= 3:
        return "high"
    if count >= 2:
        return "medium"
    return "low"


def fact_components(fact: dict[str, Any]) -> list[str]:
    relationships = fact.get("relationships", {})
    components = relationships.get("component_ids") or []
    return [component for component in components if component]


def make_evidence(concept_id: str, facts: list[dict[str, Any]], note: str, detector_class: str = "inference") -> dict[str, Any]:
    fact_ids = [fact["id"] for fact in facts if fact.get("id")]
    files = sorted({source for fact in facts for source in fact.get("source_files", [])})
    return {
        "fact_ids": fact_ids,
        "files": files,
        "method": "inferred-from-facts",
        "detector_class": detector_class,
        "note": note,
        "questions_asked": [],
    }


def group_by_kind(facts: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for fact in facts:
        grouped[fact.get("kind", "")].append(fact)
    return grouped


def infer_patterns(facts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped = group_by_kind(facts)
    patterns: list[dict[str, Any]] = []

    route_facts = grouped.get("route", [])
    route_styles: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for fact in route_facts:
        style = fact.get("raw_evidence", {}).get("style", "rest")
        route_styles[style].append(fact)

    style_to_pattern = {
        "rest": ("rest", "api"),
        "graphql": ("graphql", "api"),
        "grpc": ("grpc", "api"),
        "websocket": ("realtime", "realtime"),
        "sse": ("realtime", "realtime"),
    }
    for style, style_facts in route_styles.items():
        if style not in style_to_pattern:
            continue
        concept_id, category = style_to_pattern[style]
        patterns.append({
            "id": concept_id,
            "category": category,
            "confidence": confidence_from_count(len(style_facts)),
            "components": sorted({component for fact in style_facts for component in fact_components(fact)}),
            "evidence": make_evidence(concept_id, style_facts, f"Inferred from {len(style_facts)} {style} route facts."),
        })

    framework_facts = grouped.get("framework", [])
    framework_map = {
        "fastapi": ("input-validation", "security"),
        "django": ("input-validation", "security"),
        "nestjs": ("dependency-injection", "creational"),
    }
    for fact in framework_facts:
        framework = fact.get("raw_evidence", {}).get("framework")
        if framework not in framework_map:
            continue
        concept_id, category = framework_map[framework]
        patterns.append({
            "id": concept_id,
            "category": category,
            "confidence": "medium",
            "components": fact_components(fact),
            "evidence": make_evidence(concept_id, [fact], f"Inferred from framework context `{framework}`."),
        })

    model_facts = grouped.get("model", [])
    model_by_tech: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for fact in model_facts:
        tech = (fact.get("raw_evidence", {}) or {}).get("technology", "").lower()
        if tech:
            model_by_tech[tech].append(fact)

    tech_patterns = {
        "typeorm": ("active-record", "storage"),
        "sequelize": ("active-record", "storage"),
        "django orm": ("active-record", "storage"),
        "sqlalchemy": ("repository", "storage"),
        "prisma": ("data-mapper", "storage"),
    }
    for tech, tech_facts in model_by_tech.items():
        if tech not in tech_patterns:
            continue
        concept_id, category = tech_patterns[tech]
        patterns.append({
            "id": concept_id,
            "category": category,
            "confidence": confidence_from_count(len(tech_facts)),
            "components": sorted({component for fact in tech_facts for component in fact_components(fact)}),
            "evidence": make_evidence(concept_id, tech_facts, f"Inferred from model technology `{tech}`."),
        })

    external_client_facts = grouped.get("external-client", [])
    timeout_facts = [fact for fact in external_client_facts if fact.get("raw_evidence", {}).get("timeout")]
    retry_facts = [fact for fact in external_client_facts if fact.get("raw_evidence", {}).get("retry")]
    circuit_facts = [fact for fact in external_client_facts if fact.get("raw_evidence", {}).get("circuit_breaker")]

    resilience_map = [
        ("timeout", "resilience", timeout_facts, "Inferred from configured timeouts on external clients."),
        ("retry", "resilience", retry_facts, "Inferred from retry configuration on external clients."),
        ("circuit-breaker", "resilience", circuit_facts, "Inferred from circuit breaker configuration on external clients."),
    ]
    for concept_id, category, concept_facts, note in resilience_map:
        if not concept_facts:
            continue
        patterns.append({
            "id": concept_id,
            "category": category,
            "confidence": confidence_from_count(len(concept_facts)),
            "components": sorted({component for fact in concept_facts for component in fact_components(fact)}),
            "evidence": make_evidence(concept_id, concept_facts, note),
        })

    job_facts = grouped.get("job", [])
    if job_facts:
        patterns.append({
            "id": "scheduler",
            "category": "lifecycle",
            "confidence": confidence_from_count(len(job_facts)),
            "components": sorted({component for fact in job_facts for component in fact_components(fact)}),
            "evidence": make_evidence("scheduler", job_facts, "Inferred from cron or background job facts."),
        })

    auth_facts = grouped.get("auth-surface", [])
    auth_map = {
        "oauth-oidc": ("oauth-oidc", "security"),
        "jwt": ("token-auth", "security"),
        "session-auth": ("session-auth", "security"),
        "api-key-auth": ("api-key-auth", "security"),
        "rbac": ("rbac", "security"),
        "route-guard": ("route-guard", "security"),
    }
    for fact in auth_facts:
        tech = fact.get("raw_evidence", {}).get("technology")
        if tech not in auth_map:
            continue
        concept_id, category = auth_map[tech]
        patterns.append({
            "id": concept_id,
            "category": category,
            "confidence": "medium",
            "components": fact_components(fact),
            "evidence": make_evidence(concept_id, [fact], f"Inferred from auth surface `{tech}`."),
        })

    event_facts = grouped.get("event", [])
    if event_facts:
        patterns.append({
            "id": "event-driven",
            "category": "messaging",
            "confidence": confidence_from_count(len(event_facts)),
            "components": sorted({component for fact in event_facts for component in fact_components(fact)}),
            "evidence": make_evidence("event-driven", event_facts, "Inferred from detected event facts."),
        })

    deduped: dict[tuple[str, tuple[str, ...]], dict[str, Any]] = {}
    for pattern in patterns:
        key = (pattern["id"], tuple(pattern.get("components", [])))
        existing = deduped.get(key)
        if not existing or existing["confidence"] == "low" and pattern["confidence"] != "low":
            deduped[key] = pattern
    return sorted(deduped.values(), key=lambda item: (item["category"], item["id"]))


def infer_anti_patterns(facts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    anti_patterns: list[dict[str, Any]] = []
    grouped = group_by_kind(facts)

    route_facts = grouped.get("route", [])
    unprotected = [fact for fact in route_facts if fact.get("raw_evidence", {}).get("auth") in ("no", False, None)]
    if len(unprotected) >= 5:
        anti_patterns.append({
            "id": "god-endpoint",
            "category": "api",
            "confidence": "low",
            "components": sorted({component for fact in unprotected for component in fact_components(fact)}),
            "evidence": make_evidence("god-endpoint", unprotected[:5], "Large set of unauthenticated route facts may indicate boundary sprawl."),
        })

    import_edges = grouped.get("import-edge", [])
    cycles = [fact for fact in import_edges if fact.get("raw_evidence", {}).get("cycle")]
    if cycles:
        anti_patterns.append({
            "id": "circular-dependency",
            "category": "dependencies",
            "confidence": confidence_from_count(len(cycles)),
            "components": sorted({component for fact in cycles for component in fact_components(fact)}),
            "evidence": make_evidence("circular-dependency", cycles, "Inferred from cyclic import-edge facts."),
        })
    return anti_patterns


def infer_gaps(facts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped = group_by_kind(facts)
    external_clients = grouped.get("external-client", [])
    gaps: list[dict[str, Any]] = []
    missing_timeout = [fact for fact in external_clients if not fact.get("raw_evidence", {}).get("timeout")]
    if missing_timeout:
        gaps.append({
            "id": "timeout",
            "relevance": f"{len(missing_timeout)} external client facts have no timeout configuration.",
            "recommendation": "Add explicit timeouts to outbound HTTP, database, and broker calls.",
        })
    missing_retry = [fact for fact in external_clients if not fact.get("raw_evidence", {}).get("retry")]
    if missing_retry:
        gaps.append({
            "id": "retry",
            "relevance": f"{len(missing_retry)} external client facts have no retry policy.",
            "recommendation": "Add bounded retry behavior where idempotency and dependency semantics allow it.",
        })
    return gaps


def build_output(facts_dir: Path, facts: list[dict[str, Any]]) -> dict[str, Any]:
    domains = sorted({fact.get("domain") for fact in facts if fact.get("domain")})
    return {
        "version": "1",
        "generated_from": str(facts_dir),
        "concepts": {
            "detected_patterns": infer_patterns(facts),
            "detected_anti_patterns": infer_anti_patterns(facts),
            "gaps": infer_gaps(facts),
            "scan_metadata": {
                "facts_index": str(facts_dir / "index.json"),
                "fact_domains_used": domains,
                "tools_used": sorted({fact.get("detector", {}).get("class") for fact in facts if fact.get("detector", {}).get("class")}),
            },
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Infer Augur concepts from facts.")
    parser.add_argument("facts_dir", type=Path, help="Path to facts directory.")
    parser.add_argument("--output", type=Path, required=True, help="Output JSON path.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    facts = load_facts(args.facts_dir)
    output = build_output(args.facts_dir, facts)
    write_json(args.output, output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
