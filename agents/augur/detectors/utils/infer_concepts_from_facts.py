#!/usr/bin/env python3
"""Infer deterministic concept facts from normalized facts.

This script is intentionally pragmatic rather than exhaustive. It turns the
facts layer into normalized concept facts so Phase 1 can stay fully
deterministic while Phase 2 owns final concept judgment.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "detectors"))

from utils import component_ids_from_relationships, fact_kind, fact_payload, make_doc_ref, make_entity_ref, make_fact_ref, make_question_ref, normalize_fact_record
BUNDLED_CONCEPT_QUESTIONS = ROOT / ".generated" / "bundles" / "detectors" / "concepts" / "review_questions.json"
CONCEPT_REFERENCES_DIR = ROOT / "references" / "concepts"
FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)
SEMANTIC_REVIEW_CONCEPTS = {
    "active-record",
    "aggregate",
    "cqrs",
    "data-mapper",
    "ddd",
    "dependency-injection",
    "event-driven",
    "event-sourcing",
    "hexagonal",
    "layered",
    "microservices",
    "modular-monolith",
    "outbox",
    "plugin",
    "repository",
    "rest",
    "saga",
    "saga-orchestrator",
    "scheduler",
    "service-mesh",
    "service-manager",
    "state-machine",
    "unit-of-work",
    "workflow-engine",
}
AUTO_CONFIRM_FACT_CONCEPTS = {
    "api-key-auth",
    "circuit-breaker",
    "graphql",
    "grpc",
    "health-check",
    "input-validation",
    "oauth-oidc",
    "rbac",
    "retry",
    "realtime",
    "route-guard",
    "router",
    "session-auth",
    "structured-logging",
    "timeout",
    "token-auth",
}
DETECTOR_BACKING = {
    "repository": "strong",
    "rest": "strong",
    "workflow-engine": "partial",
    "plugin": "partial",
    "scheduler": "partial",
    "service-manager": "weak",
    "state-machine": "weak",
    "event-driven": "weak",
    "command-dispatch": "weak",
}
CONFIDENCE_ORDER = {"low": 0, "medium": 1, "high": 2}
CONFIDENCE_BY_SCORE = {0: "low", 1: "medium", 2: "high"}
FRAMEWORK_PHASE2_HINTS = {
    "react": {
        "inspect_concepts": ["component", "form-binding", "hydration", "error-boundary", "suspense-boundary"],
        "focus": "Treat React as frontend structure evidence. Inspect component boundaries, hydration/bootstrap paths, and whether state or data-fetching leaks into presentation code.",
    },
    "vue": {
        "inspect_concepts": ["component", "form-binding", "hydration", "reactive-store"],
        "focus": "Treat Vue as frontend structure evidence. Inspect component composition, template-driven form binding, hydration/SSR handoff, and reactive store usage only when grounded in code.",
    },
    "angular": {
        "inspect_concepts": ["component", "dependency-injection", "form-binding", "route-guard", "hydration"],
        "focus": "Treat Angular as frontend app-framework evidence. Inspect DI seams, router guards, and whether forms and services are framework-structured rather than ad hoc.",
    },
    "nextjs": {
        "inspect_concepts": ["hydration", "server-prefetch", "server-route-registration", "error-boundary", "suspense-boundary"],
        "focus": "Treat Next.js as full-stack frontend evidence. Inspect server/client boundaries, prefetch and hydration flow, route handlers, and whether loading or error boundaries are framework-shaped.",
    },
    "sveltekit": {
        "inspect_concepts": ["hydration", "server-prefetch", "server-route-registration", "error-boundary", "suspense-boundary"],
        "focus": "Treat SvelteKit as full-stack frontend evidence. Inspect load functions, endpoint/page coupling, hydration flow, and whether server routes are distinct from UI composition.",
    },
}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def parse_frontmatter(text: str) -> dict[str, Any]:
    match = FRONTMATTER_RE.match(text)
    if not match:
        return {}
    return yaml.safe_load(match.group(1)) or {}


def find_concept_reference(concept_id: str) -> Path:
    direct = CONCEPT_REFERENCES_DIR / f"{concept_id}.md"
    if direct.exists():
        return direct
    for path in CONCEPT_REFERENCES_DIR.rglob(f"{concept_id}.md"):
        if path.is_file():
            return path
    return direct


def concept_reference_doc(concept_id: str) -> str:
    return str(find_concept_reference(concept_id).relative_to(ROOT))


def concept_category(concept_id: str) -> str:
    path = find_concept_reference(concept_id)
    if not path.exists():
        return "framework"
    frontmatter = parse_frontmatter(path.read_text(encoding="utf-8"))
    abstraction = frontmatter.get("abstraction") or []
    if isinstance(abstraction, list):
        for entry in abstraction:
            value = str(entry).strip()
            if value:
                return value
    concept_type = str(frontmatter.get("type") or "").strip()
    return concept_type or "framework"


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def iter_fact_files(facts_path: Path) -> list[Path]:
    if facts_path.is_file():
        return [facts_path]
    index_file = facts_path.parent / "index.json"
    if index_file.exists():
        index = load_json(index_file)
        files = []
        for domain in index.get("index", {}).get("domains", []):
            rel = domain.get("file")
            if rel:
                files.append((facts_path.parent / rel).resolve())
        return [path for path in files if path.exists()]
    return sorted(p for p in facts_path.glob("*.json"))


def load_facts(facts_path: Path) -> list[dict[str, Any]]:
    facts: list[dict[str, Any]] = []
    for path in iter_fact_files(facts_path):
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
    return component_ids_from_relationships(fact.get("relationships"))


def make_evidence(concept_id: str, facts: list[dict[str, Any]], note: str, detector_class: str = "inference") -> dict[str, Any]:
    fact_ids = [fact["id"] for fact in facts if fact.get("id")]
    files = sorted({source for fact in facts for source in fact.get("source_files", [])})
    components = sorted({component for fact in facts for component in fact_components(fact)})
    fingerprint_source = "|".join(
        [
            concept_id,
            *fact_ids,
            *files,
            *components,
        ]
    )
    return {
        "fact_ids": fact_ids,
        "files": files,
        "components": components,
        "fingerprint": hashlib.sha256(fingerprint_source.encode("utf-8")).hexdigest(),
        "method": "inferred-from-facts",
        "detector_class": detector_class,
        "note": note,
        "questions_asked": [],
    }


def concept_decision_mode(concept_id: str) -> str:
    if concept_id in SEMANTIC_REVIEW_CONCEPTS:
        return "semantic-review"
    return "fact-inference"


def concept_detector_verdict(concept_id: str, confidence: str) -> str:
    if concept_id in SEMANTIC_REVIEW_CONCEPTS:
        return "candidate"
    if concept_id in AUTO_CONFIRM_FACT_CONCEPTS and confidence in {"medium", "high"}:
        return "confirmed"
    return "candidate"


def detector_backing(concept_id: str) -> str:
    if concept_id in DETECTOR_BACKING:
        return DETECTOR_BACKING[concept_id]
    reference_path = find_concept_reference(concept_id)
    if reference_path.exists():
        return "strong"
    detector_dir = ROOT / "detectors" / "concepts" / concept_id
    if detector_dir.exists():
        files = {path.name for path in detector_dir.iterdir() if path.is_file()}
        if files:
            return "partial"
    return "weak"


def cap_confidence(confidence: str, maximum: str) -> str:
    capped = min(CONFIDENCE_ORDER.get(confidence, 0), CONFIDENCE_ORDER.get(maximum, 0))
    return CONFIDENCE_BY_SCORE[capped]


def adjusted_pattern_confidence(concept_id: str, confidence: str, facts: list[dict[str, Any]]) -> str:
    adjusted = confidence
    if concept_id in {"event-driven", "scheduler"}:
        adjusted = cap_confidence(adjusted, "medium")
    if concept_id in {"service-manager", "state-machine"}:
        adjusted = cap_confidence(adjusted, "low")
    if concept_id == "workflow-engine":
        concrete_framework = any(
            fact_kind(fact) == "framework"
            or str(fact_payload(fact).get("registration_type") or "") in {"workflow-registration", "activity-registration"}
            for fact in facts
        )
        adjusted = cap_confidence(adjusted, "high" if concrete_framework else "medium")
    if concept_id == "rest":
        route_count = sum(1 for fact in facts if fact_kind(fact) == "route")
        adjusted = cap_confidence(adjusted, "medium" if route_count >= 2 else "low")
    if concept_id == "repository":
        boundary_count = sum(1 for fact in facts if fact_kind(fact) == "boundary")
        adjusted = cap_confidence(adjusted, "high" if boundary_count >= 2 else "medium")
    return adjusted


def supporting_evidence(concept_id: str, facts: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "fact_ids": [fact["id"] for fact in facts if fact.get("id")],
        "component_ids": sorted({component for fact in facts for component in fact_components(fact)}),
        "detector_backing": detector_backing(concept_id),
    }


def counter_evidence_summary(concept_id: str, facts: list[dict[str, Any]]) -> list[str]:
    counter: list[str] = []
    if concept_id == "route-guard":
        unprotected = [fact for fact in facts if fact_payload(fact).get("auth") in ("", "no", False, None)]
        if unprotected:
            counter.append(f"{len(unprotected)} route facts appear unguarded.")
    return counter


def evidence_gap_summary(concept_id: str, facts: list[dict[str, Any]]) -> list[str]:
    gaps: list[str] = []
    if concept_id in {"timeout", "retry"}:
        missing = [fact for fact in facts if not fact_payload(fact).get(concept_id)]
        if missing:
            gaps.append(f"{len(missing)} supporting facts are missing `{concept_id}` configuration.")
    if concept_id == "circuit-breaker":
        missing = [fact for fact in facts if not fact_payload(fact).get("circuit_breaker")]
        if missing:
            gaps.append(f"{len(missing)} supporting facts are missing circuit-breaker configuration.")
    return gaps


def build_pattern(
    concept_id: str,
    category: str,
    confidence: str,
    facts: list[dict[str, Any]],
    note: str,
) -> dict[str, Any]:
    components = sorted({component for fact in facts for component in fact_components(fact)})
    confidence = adjusted_pattern_confidence(concept_id, confidence, facts)
    evidence = make_evidence(concept_id, facts, note)
    grounded_in = evidence["files"]
    fact_evidence = evidence["fact_ids"]
    return {
        "id": concept_id,
        "category": category,
        "confidence": confidence,
        "components": components,
        "evidence": evidence,
        "supporting_evidence": supporting_evidence(concept_id, facts),
        "counter_evidence": counter_evidence_summary(concept_id, facts),
        "evidence_gaps": evidence_gap_summary(concept_id, facts),
        "grounded_in": grounded_in,
        "fact_evidence": fact_evidence,
        "decision_mode": concept_decision_mode(concept_id),
        "review_required": concept_decision_mode(concept_id) == "semantic-review",
    }


def group_by_kind(facts: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for fact in facts:
        grouped[fact_kind(fact)].append(fact)
    return grouped


def build_framework_review_context(framework_facts: list[dict[str, Any]]) -> dict[str, Any]:
    detected_frameworks: list[dict[str, Any]] = []
    inspect_concepts: list[str] = []
    focus_areas: list[str] = []
    concept_to_frameworks: dict[str, list[str]] = defaultdict(list)

    for fact in framework_facts:
        raw = fact_payload(fact)
        framework = str(raw.get("framework") or "").strip()
        if not framework:
            continue
        detected_frameworks.append({
            "framework": framework,
            "confidence": str(raw.get("confidence_hint") or "low"),
            "scope": str(raw.get("scope") or ""),
            "framework_kind": str(raw.get("framework_kind") or ""),
        })
        hint = FRAMEWORK_PHASE2_HINTS.get(framework)
        if not hint:
            continue
        for concept_id in hint.get("inspect_concepts", []):
            concept_name = str(concept_id or "").strip()
            if not concept_name:
                continue
            if concept_name not in inspect_concepts:
                inspect_concepts.append(concept_name)
            if framework not in concept_to_frameworks[concept_name]:
                concept_to_frameworks[concept_name].append(framework)
        focus = str(hint.get("focus") or "").strip()
        if focus and focus not in focus_areas:
            focus_areas.append(focus)

    return {
        "detected_frameworks": detected_frameworks,
        "inspect_concepts": inspect_concepts,
        "focus_areas": focus_areas,
        "concept_to_frameworks": dict(concept_to_frameworks),
    }


def infer_patterns(facts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped = group_by_kind(facts)
    patterns: list[dict[str, Any]] = []

    route_facts = grouped.get("route", [])
    route_styles: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for fact in route_facts:
        style = fact_payload(fact).get("style", "rest")
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
        patterns.append(build_pattern(
            concept_id,
            category,
            confidence_from_count(len(style_facts)),
            style_facts,
            f"Inferred from {len(style_facts)} {style} route facts.",
        ))

    framework_facts = grouped.get("framework", [])
    for fact in framework_facts:
        raw = fact_payload(fact)
        framework = str(raw.get("framework") or "")
        relationships = raw.get("relationships") if isinstance(raw.get("relationships"), dict) else {}
        for relation, confidence in (("implements", "high"), ("supports", "medium")):
            concepts = relationships.get(relation) if isinstance(relationships.get(relation), list) else []
            for concept_id in concepts:
                concept_name = str(concept_id or "").strip()
                if not concept_name:
                    continue
                patterns.append(build_pattern(
                    concept_name,
                    concept_category(concept_name),
                    confidence,
                    [fact],
                    f"Inferred from framework semantics `{framework}` relation `{relation}`.",
                ))

    model_facts = grouped.get("model", [])
    model_by_tech: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for fact in model_facts:
        tech = str(fact_payload(fact).get("technology") or "").lower()
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
        patterns.append(build_pattern(
            concept_id,
            category,
            confidence_from_count(len(tech_facts)),
            tech_facts,
            f"Inferred from model technology `{tech}`.",
        ))

    external_client_facts = grouped.get("external-client", [])
    timeout_facts = [fact for fact in external_client_facts if fact_payload(fact).get("timeout")]
    retry_facts = [fact for fact in external_client_facts if fact_payload(fact).get("retry")]
    circuit_facts = [fact for fact in external_client_facts if fact_payload(fact).get("circuit_breaker")]

    resilience_map = [
        ("timeout", "resilience", timeout_facts, "Inferred from configured timeouts on external clients."),
        ("retry", "resilience", retry_facts, "Inferred from retry configuration on external clients."),
        ("circuit-breaker", "resilience", circuit_facts, "Inferred from circuit breaker configuration on external clients."),
    ]
    for concept_id, category, concept_facts, note in resilience_map:
        if not concept_facts:
            continue
        patterns.append(build_pattern(
            concept_id,
            category,
            confidence_from_count(len(concept_facts)),
            concept_facts,
            note,
        ))

    job_facts = grouped.get("job", [])
    if job_facts:
        patterns.append(build_pattern(
            "scheduler",
            "lifecycle",
            confidence_from_count(len(job_facts)),
            job_facts,
            "Inferred from cron or background job facts.",
        ))

    registration_facts = grouped.get("registration", [])
    boundary_facts = grouped.get("boundary", [])
    dispatch_facts = grouped.get("dispatch-binding", [])

    di_facts = [
        fact
        for fact in registration_facts + boundary_facts
        if (
            fact_payload(fact).get("registration_type") in {"service-registration", "bean-registration"}
            or fact_payload(fact).get("boundary_type") in {"interface", "implementation"}
        )
    ]
    if len(di_facts) >= 3:
        patterns.append(build_pattern(
            "dependency-injection",
            "creational",
            confidence_from_count(len(di_facts)),
            di_facts[:20],
            "Inferred from service or bean registrations combined with interface boundaries.",
        ))

    repository_facts = [
        fact
        for fact in boundary_facts + grouped.get("model", [])
        if (
            fact_payload(fact).get("boundary_type") == "repository-boundary"
            or str(fact_payload(fact).get("interface", "")).endswith(("Repository", "Store", "Gateway", "Port"))
            or fact_payload(fact).get("technology") in {"jpa", "gorm", "entity-framework", "sqlalchemy"}
        )
    ]
    if len(repository_facts) >= 2:
        patterns.append(build_pattern(
            "repository",
            "storage",
            confidence_from_count(len(repository_facts)),
            repository_facts[:20],
            "Inferred from repository-like boundaries and persistence models.",
        ))

    plugin_facts = [
        fact
        for fact in registration_facts + dispatch_facts + boundary_facts
        if (
            str(fact_payload(fact).get("registration_type", "")).startswith("plugin-")
            or str(fact_payload(fact).get("binding_type", "")).startswith("plugin-")
            or str(fact_payload(fact).get("boundary_type", "")).startswith("plugin-")
        )
    ]
    if len(plugin_facts) >= 3:
        patterns.append(build_pattern(
            "plugin",
            "extensibility",
            confidence_from_count(len(plugin_facts)),
            plugin_facts[:25],
            "Inferred from plugin host, plugin registration, or plugin protocol facts.",
        ))

    workflow_facts = [
        fact
        for fact in registration_facts + dispatch_facts + grouped.get("handler", [])
        if (
            fact_payload(fact).get("registration_type") in {"workflow-registration", "activity-registration"}
            or fact_payload(fact).get("handler_type") == "workflow-handler"
            or fact_payload(fact).get("binding_type") in {"queue-binding", "topic-subscription", "topic-publish"}
        )
    ]
    if len(workflow_facts) >= 3:
        patterns.append(build_pattern(
            "workflow-engine",
            "lifecycle",
            confidence_from_count(len(workflow_facts)),
            workflow_facts[:20],
            "Inferred from workflow registration, workflow handlers, and queue or topic bindings.",
        ))

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
        tech = fact_payload(fact).get("technology")
        if tech not in auth_map:
            continue
        concept_id, category = auth_map[tech]
        patterns.append(build_pattern(
            concept_id,
            category,
            "medium",
            [fact],
            f"Inferred from auth surface `{tech}`.",
        ))

    event_facts = grouped.get("event", [])
    if event_facts:
        patterns.append(build_pattern(
            "event-driven",
            "messaging",
            confidence_from_count(len(event_facts)),
            event_facts,
            "Inferred from detected event facts.",
        ))

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
    unprotected = [fact for fact in route_facts if fact_payload(fact).get("auth") in ("no", False, None)]
    if len(unprotected) >= 5:
        anti_patterns.append({
            "id": "god-endpoint",
            "category": "api",
            "confidence": "low",
            "components": sorted({component for fact in unprotected for component in fact_components(fact)}),
            "evidence": make_evidence("god-endpoint", unprotected[:5], "Large set of unauthenticated route facts may indicate boundary sprawl."),
        })

    import_edges = grouped.get("import-edge", [])
    cycles = [fact for fact in import_edges if fact_payload(fact).get("cycle")]
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
    missing_timeout = [fact for fact in external_clients if not fact_payload(fact).get("timeout")]
    if missing_timeout:
        gaps.append({
            "id": "timeout",
            "relevance": f"{len(missing_timeout)} external client facts have no timeout configuration.",
            "recommendation": "Add explicit timeouts to outbound HTTP, database, and broker calls.",
        })
    missing_retry = [fact for fact in external_clients if not fact_payload(fact).get("retry")]
    if missing_retry:
        gaps.append({
            "id": "retry",
            "relevance": f"{len(missing_retry)} external client facts have no retry policy.",
            "recommendation": "Add bounded retry behavior where idempotency and dependency semantics allow it.",
        })
    return gaps


def metadata_from_facts_path(facts_path: Path, facts: list[dict[str, Any]]) -> dict[str, Any]:
    index_path = facts_path.parent / "index.json" if facts_path.is_dir() else facts_path
    try:
      payload = load_json(index_path)
    except Exception:
      payload = {}
    if not isinstance(payload, dict):
      payload = {}
    return {
        "version": str(payload.get("version") or "1"),
        "generated": payload.get("generated"),
        "project": payload.get("project"),
        "analysis_mode": payload.get("analysis_mode"),
        "root": payload.get("root"),
        "metadata": payload.get("metadata") if isinstance(payload.get("metadata"), dict) else {},
        "framework_context": sorted({ctx for fact in facts for ctx in (fact.get("framework_context") or []) if isinstance(ctx, str) and ctx}),
    }


def load_concept_question_bundle() -> dict[str, Any]:
    if not BUNDLED_CONCEPT_QUESTIONS.exists():
        return {}
    try:
        payload = load_json(BUNDLED_CONCEPT_QUESTIONS)
    except Exception:
        return {}
    concepts = payload.get("concepts")
    return concepts if isinstance(concepts, dict) else {}


def review_questions_for_pattern(pattern: dict[str, Any], question_bundle: dict[str, Any]) -> dict[str, Any]:
    concept_id = str(pattern.get("id") or "")
    bundled = question_bundle.get(concept_id)
    if not isinstance(bundled, dict):
        return {
            "enabled": False,
            "threshold": None,
            "ask_when": [],
            "entries": [],
        }
    questions = bundled.get("review_questions") if isinstance(bundled.get("review_questions"), dict) else {}
    entries = questions.get("entries") if isinstance(questions.get("entries"), list) else []
    entry_ids = [entry.get("id") for entry in entries if isinstance(entry, dict) and entry.get("id")]
    return {
        "enabled": bool(questions.get("enabled", False)),
        "threshold": questions.get("threshold"),
        "ask_when": list(questions.get("ask_when") or []),
        "entries": entries,
        "entry_ids": entry_ids,
        "recommended_next_step": "answer_questions" if entries else "none",
    }


def pattern_to_fact(pattern: dict[str, Any], question_bundle: dict[str, Any], framework_review_context: dict[str, Any]) -> dict[str, Any]:
    evidence = pattern.get("evidence") or {}
    question_payload = review_questions_for_pattern(pattern, question_bundle)
    concept_id = str(pattern.get("id") or "")
    heuristic_frameworks = framework_review_context.get("concept_to_frameworks", {}).get(concept_id, [])
    raw_evidence = {
        "concept_id": concept_id,
        "category": pattern.get("category"),
        "inference_method": evidence.get("method") or "inferred-from-facts",
        "note": evidence.get("note") or "",
        "fingerprint": evidence.get("fingerprint") or "",
        "decision_mode": pattern.get("decision_mode") or "fact-inference",
        "framework_heuristics": {
            "suggested_by_frameworks": heuristic_frameworks,
            "heuristic_only": bool(heuristic_frameworks),
            "inspect_next": [
                item
                for item in framework_review_context.get("inspect_concepts", [])
                if item != concept_id
            ][:8] if heuristic_frameworks else [],
            "focus_areas": framework_review_context.get("focus_areas", [])[:6] if heuristic_frameworks else [],
        },
    }
    fingerprint_source = "|".join(
        [
            str(pattern.get("id") or ""),
            *(str(item) for item in (evidence.get("fact_ids") or [])),
            *(str(item) for item in (evidence.get("files") or [])),
        ]
    )
    fact_id = f"concept-{hashlib.sha256(fingerprint_source.encode('utf-8')).hexdigest()[:10]}"
    relationships: list[dict[str, str]] = []
    for component_id in pattern.get("components") or []:
        relation = make_entity_ref("component", str(component_id), "grounded_in_component")
        if relation:
            relationships.append(relation)
    for supporting_fact_id in evidence.get("fact_ids") or []:
        relation = make_fact_ref(str(supporting_fact_id), "derived_from")
        if relation:
            relationships.append(relation)
    relation = make_doc_ref(concept_reference_doc(concept_id), "relevant_concept")
    if relation:
        relationships.append(relation)
    for framework_name in heuristic_frameworks:
        relation = make_doc_ref(f"references/frameworks/{framework_name}.md", "relevant_framework")
        if relation:
            relationships.append(relation)
    question_ids: list[str] = []
    for entry in question_payload.get("entries") or []:
        if not isinstance(entry, dict):
            continue
        qid = str(entry.get("id") or "").strip()
        if not qid:
            continue
        question_ids.append(qid)
        relation = make_question_ref(qid)
        if relation:
            relationships.append(relation)

    return normalize_fact_record({
        "id": fact_id,
        "kind": "concept-candidate",
        "domain": "concepts",
        "summary": f"Candidate concept `{pattern.get('id')}` inferred from deterministic facts.",
        "source_files": list(evidence.get("files") or []),
        "detector": {
            "id": f"concepts-{pattern.get('id')}",
            "class": "inference",
            "strength": {
                "strong": 5,
                "partial": 3,
                "weak": 2,
            }.get(str((pattern.get("supporting_evidence") or {}).get("detector_backing") or detector_backing(concept_id)), 3),
            "rule": None,
            "bundle": "detectors:concepts",
        },
        "raw_evidence": {
            **raw_evidence,
            "confidence_hint": str(pattern.get("confidence") or "low"),
            "detector_backing": str((pattern.get("supporting_evidence") or {}).get("detector_backing") or detector_backing(concept_id)),
            "counter_evidence": list(pattern.get("counter_evidence") or []),
            "evidence_gaps": list(pattern.get("evidence_gaps") or []),
            "review": {
                "required": bool(pattern.get("review_required")),
                "questions": question_payload,
            },
            "evidence_summary": {
                "supporting": dict(pattern.get("supporting_evidence") or {}),
                "counter": list(pattern.get("counter_evidence") or []),
                "gaps": list(pattern.get("evidence_gaps") or []),
                "question_ids": question_ids,
            },
        },
        "relationships": relationships,
    })


def gap_to_fact(gap: dict[str, Any]) -> dict[str, Any]:
    gap_id = str(gap.get("id") or "unknown-gap")
    relationships: list[dict[str, str]] = []
    relation = make_doc_ref(concept_reference_doc(gap_id), "relevant_concept")
    if relation:
        relationships.append(relation)
    return normalize_fact_record({
        "id": f"concept-gap-{gap_id}",
        "kind": "concept-gap",
        "domain": "concepts",
        "summary": str(gap.get("relevance") or f"Gap detected for concept `{gap_id}`."),
        "source_files": [],
        "detector": {
            "id": f"concept-gap-{gap_id}",
            "class": "inference",
            "strength": 2,
            "rule": None,
            "bundle": "detectors:concepts",
        },
        "raw_evidence": {
            "concept_id": gap_id,
            "recommendation": str(gap.get("recommendation") or ""),
            "kind": "gap",
            "confidence_hint": "medium",
            "review": {
                "required": False,
                "questions": {
                    "enabled": False,
                    "threshold": None,
                    "ask_when": [],
                    "entries": [],
                    "entry_ids": [],
                    "recommended_next_step": "none",
                },
            },
        },
        "relationships": relationships,
    })


def build_output(facts_path: Path, facts: list[dict[str, Any]]) -> dict[str, Any]:
    meta = metadata_from_facts_path(facts_path, facts)
    patterns = infer_patterns(facts)
    gaps = infer_gaps(facts)
    question_bundle = load_concept_question_bundle()
    framework_review_context = build_framework_review_context(group_by_kind(facts).get("framework", []))
    concept_facts = [pattern_to_fact(pattern, question_bundle, framework_review_context) for pattern in patterns]
    concept_facts.extend(gap_to_fact(gap) for gap in gaps)
    detectors: dict[str, dict[str, Any]] = {}
    normalized_facts: list[dict[str, Any]] = []
    question_bundle = load_question_bundle()
    for fact in concept_facts:
        detector_id = str(fact.get("detector_id") or "").strip()
        normalized = dict(fact)
        normalized.pop("domain", None)
        normalized_facts.append(normalized)
        concept_id = str((fact.get("fact") or {}).get("concept_id") or "").strip()
        bundle_entry = question_bundle.get(concept_id) if concept_id else {}
        detectors[detector_id] = {
            "id": detector_id,
            "kind": str((fact.get("fact") or {}).get("kind") or "").strip() or None,
            "class": "bridge",
            "strength": None,
            "rule": None,
            "bundle": "detectors:concepts",
            "docs": list((bundle_entry or {}).get("docs") or ([concept_reference_doc(concept_id)] if concept_id else [])),
            "review_questions": [
                str(entry.get("prompt") or "").strip()
                for entry in (((bundle_entry or {}).get("review_questions") or {}).get("entries") or [])
                if isinstance(entry, dict) and str(entry.get("prompt") or "").strip()
            ],
        }

    return {
        "version": meta["version"],
        "generated": meta["generated"],
        "project": meta["project"],
        "analysis_mode": meta["analysis_mode"],
        "domain": "concepts",
        "detectors": detectors,
        "count": len(normalized_facts),
        "facts": normalized_facts,
        "metadata": {
            **meta["metadata"],
            "generated_from": str(facts_path),
            "fact_domains_used": sorted({fact.get("domain") for fact in facts if fact.get("domain")}),
            "tools_used": [],
            "framework_review_context": framework_review_context,
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Infer Augur concepts from facts.")
    parser.add_argument("facts_dir", type=Path, help="Path to facts directory or a single facts payload JSON file.")
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
