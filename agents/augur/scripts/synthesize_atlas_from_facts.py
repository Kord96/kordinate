#!/usr/bin/env python3
"""Synthesize an atlas fragment from Augur facts.

This CLI reads normalized facts from `facts/` and derives the atlas sections
that can be built directly from first-order evidence:

- component hierarchy
- domain_model hints
- flows
- state
- external_dependencies
- optional module_graph support data

It is intentionally conservative. It does not infer concepts or tensions, and
it does not try to recreate full architectural narration. That remains the job
of the concept layer and the atlas composer.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]


LANGUAGE_BY_SUFFIX = {
    ".py": "Python",
    ".js": "JavaScript",
    ".jsx": "JavaScript",
    ".ts": "TypeScript",
    ".tsx": "TypeScript",
    ".go": "Go",
    ".rs": "Rust",
    ".rb": "Ruby",
    ".php": "PHP",
    ".cs": "C#",
    ".java": "Java",
    ".kt": "Kotlin",
    ".scala": "Scala",
    ".swift": "Swift",
    ".ex": "Elixir",
    ".exs": "Elixir",
}


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=False) + "\n", encoding="utf-8")


def slugify(value: str) -> str:
    cleaned = []
    last_dash = False
    for char in value.lower():
        if char.isalnum():
            cleaned.append(char)
            last_dash = False
        else:
            if not last_dash:
                cleaned.append("-")
                last_dash = True
    slug = "".join(cleaned).strip("-")
    return slug or "unknown"


def source_path(path: str) -> str:
    return path.split(":", 1)[0]


def source_line(path: str) -> str:
    parts = path.rsplit(":", 1)
    if len(parts) == 2 and parts[1].isdigit():
        return path
    return path


def source_dir(path: str) -> str:
    return source_path(path)


def unique_strings(values: list[str]) -> list[str]:
    seen: dict[str, None] = {}
    for value in values:
        if value and value not in seen:
            seen[value] = None
    return list(seen.keys())


def normalize_symbol(value: str) -> str:
    return "".join(char.lower() for char in value if char.isalnum())


def symbol_variants(*values: str) -> set[str]:
    variants: set[str] = set()
    for value in values:
        raw = str(value or "").strip()
        if not raw:
            continue
        variants.add(normalize_symbol(raw))
        if "::" in raw:
            variants.add(normalize_symbol(raw.split("::")[-1]))
        if ":" in raw:
            variants.add(normalize_symbol(raw.split(":")[-1]))
        if "." in raw:
            variants.add(normalize_symbol(raw.split(".")[-1]))
    variants.discard("")
    return variants


def symbols_overlap(*groups: tuple[str, ...] | list[str] | set[str] | str) -> bool:
    left: set[str] = set()
    right: set[str] = set()
    if len(groups) < 2:
        return False
    first = groups[0]
    second = groups[1]
    for value in (first if isinstance(first, (list, tuple, set)) else [first]):
        left.update(symbol_variants(str(value)))
    for value in (second if isinstance(second, (list, tuple, set)) else [second]):
        right.update(symbol_variants(str(value)))
    if not left or not right:
        return False
    return bool(left & right)


def merge_failure_modes(failure_modes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    merged: dict[str, dict[str, Any]] = {}
    for item in failure_modes:
        if not isinstance(item, dict):
            continue
        failure_id = str(item.get("id") or "")
        if not failure_id:
            continue
        bucket = merged.setdefault(
            failure_id,
            {
                "id": failure_id,
                "trigger": str(item.get("trigger") or ""),
                "impact": str(item.get("impact") or ""),
                "signals": [],
                "gaps": [],
                "recovery": [],
                "severity": str(item.get("severity") or "low"),
                "grounded_in": [],
            },
        )
        bucket["signals"] = unique_strings(bucket["signals"] + [str(v) for v in item.get("signals") or [] if v])
        bucket["gaps"] = unique_strings(bucket["gaps"] + [str(v) for v in item.get("gaps") or [] if v])
        bucket["recovery"] = unique_strings(bucket["recovery"] + [str(v) for v in item.get("recovery") or [] if v])
        bucket["grounded_in"] = unique_strings(bucket["grounded_in"] + [source_line(str(v)) for v in item.get("grounded_in") or [] if v])
    return list(merged.values())


def normalize_health_block(target: dict[str, Any]) -> None:
    health = target.get("health")
    if not isinstance(health, dict):
        return
    health["failure_modes"] = merge_failure_modes(health.get("failure_modes") or [])
    health["gaps"] = unique_strings([str(v) for v in health.get("gaps") or [] if v])


def coerce_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value != 0
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "y", "on"}
    return bool(value)


def is_test_path(path: str) -> bool:
    lowered = source_path(path).lower()
    name = Path(lowered).name
    return (
        lowered.startswith("test/")
        or lowered.startswith("tests/")
        or lowered.endswith("_test.go")
        or lowered.endswith("_test.py")
        or lowered.endswith(".spec.ts")
        or lowered.endswith(".spec.tsx")
        or lowered.endswith(".test.ts")
        or lowered.endswith(".test.tsx")
        or lowered.endswith(".spec.js")
        or lowered.endswith(".test.js")
        or "/test/" in lowered
        or "/tests/" in lowered
        or name.startswith("test_")
    )


def is_tooling_path(path: str) -> bool:
    lowered = source_path(path).lower()
    return (
        lowered.startswith(".github/")
        or lowered.startswith("tools/")
        or lowered.startswith("scripts/")
        or "/tools/" in lowered
        or "/scripts/" in lowered
    )


def should_keep_grounded_sources(sources: list[str]) -> list[str]:
    grounded = [source_line(item) for item in sources if item]
    if not grounded:
        return []
    filtered = [item for item in grounded if not is_test_path(item) and not is_tooling_path(item)]
    return filtered or []


def is_internal_route_path(path: str) -> bool:
    lowered = path.strip().lower()
    return any(
        token in lowered
        for token in (
            "/metrics",
            "/health",
            "/healthz",
            "/ready",
            "/readyz",
            "/live",
            "/livez",
            "/debug",
            "/pprof",
            "/swagger",
            "/openapi",
            "/docs",
        )
    )


def derive_flow_business_metrics(flow: dict[str, Any]) -> list[dict[str, Any]]:
    grounded_in = [source_line(str(item)) for item in flow.get("grounded_in") or [] if item]
    if not grounded_in:
        return []
    flow_id = str(flow.get("id") or "flow")
    flow_type = str(flow.get("type") or "")
    trigger = str(flow.get("trigger") or "").lower()
    name = str(flow.get("name") or "")
    actors = {str(item) for item in flow.get("actors") or [] if item}

    if flow_type == "control" and trigger in {"workflow", "background"}:
        return []
    if "api-client" not in actors:
        return []
    if is_internal_route_path(name):
        return []

    metrics = [
        {
            "name": f"{flow_id}.completed",
            "description": f"Successful completions of the {name} flow.",
            "owner": flow_id,
            "grounded_in": grounded_in,
        }
    ]
    return metrics


def normalize_fact(raw: Any) -> dict[str, Any] | None:
    if not isinstance(raw, dict):
        return None

    source_files = raw.get("source_files") or raw.get("grounded_in") or []
    if isinstance(source_files, str):
        source_files = [source_files]
    if not isinstance(source_files, list):
        source_files = []

    relationships = raw.get("relationships") or {}
    if not isinstance(relationships, dict):
        relationships = {}

    detector = raw.get("detector") or {}
    if not isinstance(detector, dict):
        detector = {}

    return {
        "id": str(raw.get("id") or slugify(f"{raw.get('kind', 'fact')}::{source_files[0] if source_files else 'unknown'}")),
        "kind": str(raw.get("kind") or "fact"),
        "domain": str(raw.get("domain") or "unknown"),
        "summary": str(raw.get("summary") or ""),
        "confidence": str(raw.get("confidence") or "low"),
        "framework_context": [str(item) for item in raw.get("framework_context") or [] if item],
        "source_files": [str(item) for item in source_files if item],
        "detector": {
            "id": str(detector.get("id") or "unknown"),
            "class": str(detector.get("class") or "inference"),
            "strength": int(detector.get("strength") or 1),
            "rule": detector.get("rule"),
            "bundle": detector.get("bundle"),
        },
        "raw_evidence": raw.get("raw_evidence") if isinstance(raw.get("raw_evidence"), dict) else {},
        "negative_evidence": [str(item) for item in raw.get("negative_evidence") or [] if item],
        "contradictions": [str(item) for item in raw.get("contradictions") or [] if item],
        "relationships": {
            "component_ids": [str(item) for item in relationships.get("component_ids") or [] if item],
            "depends_on_fact_ids": [str(item) for item in relationships.get("depends_on_fact_ids") or [] if item],
            "related_fact_ids": [str(item) for item in relationships.get("related_fact_ids") or [] if item],
        },
    }


def load_fact_documents(facts_root: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    documents: list[dict[str, Any]] = []
    index: dict[str, Any] = {}

    if facts_root.is_file():
        payload = read_json(facts_root)
        if isinstance(payload, dict):
            index = payload if facts_root.name == "index.json" else {}
            documents.append(payload)
        elif isinstance(payload, list):
            documents.append({"facts": payload})
        return index, documents

    if not facts_root.exists():
        return index, documents

    index_path = facts_root / "index.json"
    if index_path.exists():
        payload = read_json(index_path)
        if isinstance(payload, dict):
            index = payload
            documents.append(payload)
    for path in sorted(facts_root.glob("*.json")):
        if path.name == "index.json":
            continue
        payload = read_json(path)
        if isinstance(payload, dict) or isinstance(payload, list):
            documents.append(payload if isinstance(payload, dict) else {"facts": payload})

    # Some future layouts may store subdirectories with domain JSON documents.
    for path in sorted(facts_root.rglob("*.json")):
        if path == index_path or path.parent == facts_root:
            continue
        payload = read_json(path)
        if isinstance(payload, dict) or isinstance(payload, list):
            documents.append(payload if isinstance(payload, dict) else {"facts": payload})

    return index, documents


def collect_facts(documents: list[dict[str, Any]]) -> list[dict[str, Any]]:
    facts: list[dict[str, Any]] = []
    for document in documents:
        if not isinstance(document, dict):
            continue
        if isinstance(document.get("facts"), list):
            for item in document["facts"]:
                normalized = normalize_fact(item)
                if normalized:
                    facts.append(normalized)
        elif isinstance(document.get("kind"), str) and "id" in document:
            normalized = normalize_fact(document)
            if normalized:
                facts.append(normalized)
        elif isinstance(document.get("index"), dict) and isinstance(document["index"].get("facts"), list):
            for item in document["index"]["facts"]:
                normalized = normalize_fact(item)
                if normalized:
                    facts.append(normalized)
    return facts


def load_detected_patterns(facts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    patterns: list[dict[str, Any]] = []
    for item in facts:
        if not isinstance(item, dict):
            continue
        if item.get("kind") != "concept-candidate":
            continue
        raw = item.get("raw_evidence") or {}
        if not isinstance(raw, dict):
            continue
        concept_id = raw.get("concept_id")
        if not isinstance(concept_id, str) or not concept_id:
            continue
        patterns.append({
            "id": concept_id,
            "category": str(raw.get("category") or "unknown"),
            "confidence": str(item.get("confidence") or "low"),
            "components": item.get("relationships", {}).get("component_ids") if isinstance(item.get("relationships"), dict) else [],
            "evidence": {
                "fact_ids": raw.get("supporting_fact_ids") or item.get("relationships", {}).get("depends_on_fact_ids") if isinstance(item.get("relationships"), dict) else [],
                "files": item.get("source_files") or [],
                "components": raw.get("supporting_components") or [],
                "method": raw.get("inference_method") or "inferred-from-facts",
                "note": raw.get("note") or "",
            },
        })
    return patterns


def load_monitoring_index() -> dict[str, dict[str, Any]]:
    candidates = [
        ROOT / ".generated" / "bundles" / "detectors" / "concept-evidence" / "monitoring.json",
        ROOT / "bundles" / "detectors" / "concept-evidence" / "monitoring.json",
    ]
    for path in candidates:
        if not path.exists():
            continue
        payload = read_json(path)
        if not isinstance(payload, dict):
            continue
        concepts = payload.get("concepts") or {}
        return concepts if isinstance(concepts, dict) else {}
    return {}


def classify_language(path: str) -> str | None:
    suffix = Path(source_path(path)).suffix.lower()
    return LANGUAGE_BY_SUFFIX.get(suffix)


def classify_store_concept(text: str) -> str:
    lowered = text.lower()
    if any(token in lowered for token in ["redis", "cache", "memcache"]):
        return "cache"
    if any(token in lowered for token in ["kafka", "rabbit", "queue", "broker", "pubsub", "pub-sub"]):
        return "message-broker"
    if any(token in lowered for token in ["s3", "blob", "object", "bucket", "minio"]):
        return "object-store"
    if any(token in lowered for token in ["mongo", "document", "jsonb"]):
        return "document-store"
    if any(token in lowered for token in ["duckdb", "olap", "warehouse", "analytics"]):
        return "embedded-olap"
    if any(token in lowered for token in ["sqlite", "postgres", "mysql", "sql", "rdbms", "relational"]):
        return "relational-db"
    if any(token in lowered for token in ["file", "filesystem", "path", "disk"]):
        return "filesystem"
    return "in-memory"


def classify_dependency_concept(text: str) -> str:
    lowered = text.lower()
    if any(token in lowered for token in ["grpc"]):
        return "grpc"
    if any(token in lowered for token in ["redis", "cache", "memcache"]):
        return "cache"
    if any(token in lowered for token in ["kafka", "rabbit", "queue", "broker", "pubsub", "pub-sub"]):
        return "message-broker"
    if any(token in lowered for token in ["s3", "blob", "object", "bucket", "minio"]):
        return "object-store"
    if any(token in lowered for token in ["auth", "oidc", "oauth", "jwt", "identity"]):
        return "auth-provider"
    if any(token in lowered for token in ["smtp", "mail"]):
        return "smtp"
    if any(token in lowered for token in ["dns"]):
        return "dns"
    return "http-api"


def infer_api_style(route_facts: list[dict[str, Any]]) -> str:
    styles = Counter()
    for fact in route_facts:
        raw = fact.get("raw_evidence") or {}
        default_style = {
            "route": "rest",
            "graphql-operation": "graphql",
            "grpc-service": "grpc",
            "websocket-channel": "websocket",
        }.get(fact.get("kind"), "rest")
        style = str(raw.get("style") or default_style).lower()
        styles[style] += 1
    if not styles:
        return "unknown"
    if len(styles) == 1:
        return next(iter(styles))
    return "mixed"


def build_frameworks(facts: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[str]]:
    framework_facts = [fact for fact in facts if fact["kind"] == "framework"]
    language_counter: Counter[str] = Counter()
    frameworks: list[dict[str, Any]] = []
    seen = set()

    for fact in framework_facts:
        raw = fact.get("raw_evidence") or {}
        name = str(raw.get("framework") or raw.get("name") or fact["summary"] or fact["id"] or "unknown")
        key = name.lower()
        if key in seen:
            continue
        seen.add(key)

        concepts = []
        if isinstance(raw.get("concepts"), list):
            concepts = unique_strings([str(item) for item in raw["concepts"] if item])
        elif isinstance(raw.get("concept"), str):
            concepts = [str(raw["concept"])]

        language = str(raw.get("language") or "").strip()
        if language:
            language_counter[language] += 1
        for source in fact.get("source_files", []):
            inferred = classify_language(source)
            if inferred:
                language_counter[inferred] += 1

        frameworks.append({"name": name, "concepts": concepts})

    return frameworks, list(language_counter.keys())


def build_routes(facts: list[dict[str, Any]]) -> tuple[dict[str, Any], list[str]]:
    route_kinds = {"route", "graphql-operation", "grpc-service", "websocket-channel"}
    route_facts = [fact for fact in facts if fact["kind"] in route_kinds]
    endpoints = []
    frameworks: list[str] = []

    for fact in route_facts:
        raw = fact.get("raw_evidence") or {}
        if fact.get("framework_context"):
            frameworks.extend(fact["framework_context"])
        style = str(raw.get("style") or fact["kind"]).lower()
        method = str(raw.get("method") or raw.get("http_method") or "GET").upper()
        path = str(raw.get("path") or raw.get("route") or raw.get("endpoint") or "").strip()
        handler = str(raw.get("handler") or raw.get("resolver") or raw.get("service") or "").strip()
        source = fact.get("source_files", [""])[0] if fact.get("source_files") else ""
        auth = raw.get("auth")
        validation = raw.get("validation")

        endpoints.append(
            {
                "method": method,
                "path": path,
                "handler": handler,
                "file": source,
                "auth": auth if auth is not None else "unknown",
                "validation": validation if validation is not None else "unknown",
            }
        )

    critical = []
    recommended = []
    minor = []
    for endpoint in endpoints:
        if endpoint["auth"] in {"no", "false", False}:
            critical.append(
                {
                    "severity": "critical",
                    "detail": f"Endpoint {endpoint['method']} {endpoint['path']} is missing explicit auth.",
                    "path": endpoint["file"],
                }
            )
        elif endpoint["auth"] == "unknown":
            recommended.append(
                {
                    "severity": "recommended",
                    "detail": f"Endpoint {endpoint['method']} {endpoint['path']} has no explicit auth fact.",
                    "path": endpoint["file"],
                }
            )

        if endpoint["validation"] in {"no", "false", False, "unknown"}:
            minor.append(
                {
                    "severity": "minor",
                    "detail": f"Endpoint {endpoint['method']} {endpoint['path']} has incomplete validation evidence.",
                    "path": endpoint["file"],
                }
            )

    api_surface = {
        "style": infer_api_style(route_facts),
        "frameworks": [{"name": fw, "version": ""} for fw in unique_strings(frameworks)],
        "endpoints": endpoints,
        "findings": {
            "critical": critical,
            "recommended": recommended,
            "minor": minor,
        },
    }

    return api_surface, unique_strings(frameworks)


def build_domain_model(facts: list[dict[str, Any]]) -> dict[str, Any]:
    model_facts = [fact for fact in facts if fact["kind"] in {"model", "state-store"}]
    entities: list[str] = []
    relationships: list[str] = []
    contexts: dict[str, dict[str, Any]] = {}

    for fact in model_facts:
        raw = fact.get("raw_evidence") or {}
        entity = raw.get("entity") or raw.get("name") or fact["summary"]
        if entity:
            entities.append(str(entity))
        rels = raw.get("relations") or raw.get("relationships") or []
        if isinstance(rels, list):
            relationships.extend([str(rel) for rel in rels if rel])
        elif isinstance(rels, str):
            relationships.append(rels)

        context_id = slugify(str(raw.get("bounded_context") or raw.get("domain") or fact.get("domain") or "derived-context"))
        context = contexts.setdefault(
            context_id,
            {
                "id": context_id,
                "name": str(raw.get("bounded_context") or raw.get("domain") or "Derived Context").replace("-", " ").title(),
                "description": "Context inferred from extracted model facts.",
                "entities": [],
                "modules": [],
                "ubiquitous_language": {},
            },
        )
        if entity:
            context["entities"].append(str(entity))
            context["ubiquitous_language"][str(entity)] = f"Entity inferred from {fact['id']}"
        context["modules"].extend(
            [source_path(source) for source in fact.get("source_files", []) if source]
        )

    if model_facts:
        primary = "catalog"
        hints = "Derived from model and state facts."
        combined = " ".join(
            [str(f.get("summary", "")) for f in model_facts]
            + [str((f.get("raw_evidence") or {}).get("technology", "")) for f in model_facts]
        ).lower()
        if any(token in combined for token in ["event", "append", "snapshot"]):
            primary = "event-sourcing"
        elif any(token in combined for token in ["graph", "node", "edge"]):
            primary = "graph"
        elif any(token in combined for token in ["cache"]):
            primary = "cache"
        domain_model = {
            "primary": primary,
            "description": hints,
            "entities": unique_strings(entities),
            "relationships": unique_strings(relationships),
            "bounded_contexts": list(contexts.values()),
        }
    else:
        domain_model = {
            "primary": "catalog",
            "description": "No model facts were available; this is a scaffold.",
            "entities": [],
            "relationships": [],
            "bounded_contexts": [],
        }

    return domain_model


def build_state_entries(facts: list[dict[str, Any]], joern: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    state_facts = [fact for fact in facts if fact["kind"] in {"model", "state-store"}]
    entries = []
    for fact in state_facts:
        raw = fact.get("raw_evidence") or {}
        technology = str(raw.get("technology") or raw.get("store") or "unknown")
        concept = classify_store_concept(technology + " " + fact.get("summary", ""))
        component_ids = fact.get("relationships", {}).get("component_ids") or []
        component = component_ids[0] if component_ids else "unknown"
        entry = (
            {
                "id": slugify(f"{fact['id']}-{technology}"),
                "concept": concept,
                "technology": technology,
                "component": component,
                "stores": str(raw.get("entity") or raw.get("stores") or fact.get("summary") or ""),
                "purpose": str(raw.get("store_purpose") or raw.get("purpose") or "derived"),
                "persistence": str(raw.get("persistence") or "persistent"),
                "readers": [str(item) for item in raw.get("readers") or [] if item],
                "writers": [str(item) for item in raw.get("writers") or [] if item],
                "grounded_in": fact.get("source_files", []),
                "schema_evolution": {
                    "migrations": raw.get("migration_path"),
                    "strategy": str(raw.get("schema_strategy") or raw.get("strategy") or "none"),
                    "tools": raw.get("tools"),
                },
                "concurrency": {
                    "strategy": str(raw.get("concurrency") or "none"),
                    "mechanism": raw.get("mechanism"),
                    "conflicts": str(raw.get("conflicts") or "unknown"),
                },
            }
        )
        if joern:
            evidence_terms = [
                entry["technology"],
                str(entry["stores"]),
                str(raw.get("entity") or ""),
                str(raw.get("target") or ""),
            ]
            readers = set(entry["readers"])
            writers = set(entry["writers"])
            grounded = set(entry["grounded_in"])
            for touch in joern.get("data_touches", []):
                touch_raw = touch.get("raw_evidence") or {}
                target_parts = [
                    str(touch_raw.get("target_name") or ""),
                    str(touch_raw.get("target_full_name") or ""),
                    str(touch_raw.get("target_code") or ""),
                ]
                if not any(symbols_overlap(evidence_terms, part) for part in target_parts if part):
                    continue
                component_ids = touch.get("relationships", {}).get("component_ids") or []
                if not component_ids:
                    continue
                if str(touch_raw.get("touch_kind") or "") == "write":
                    writers.update(str(item) for item in component_ids if item)
                else:
                    readers.update(str(item) for item in component_ids if item)
                owner_file = str(touch_raw.get("owner_file") or "")
                line_number = int(touch_raw.get("line_number", -1) or -1)
                if owner_file:
                    grounded.add(source_line(f"{owner_file}:{line_number}" if line_number > 0 else owner_file))
            entry["readers"] = sorted(readers)
            entry["writers"] = sorted(writers)
            entry["grounded_in"] = sorted(grounded)
        entries.append(entry)
    return entries


def build_external_dependencies(facts: list[dict[str, Any]], joern: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    dependency_facts = [fact for fact in facts if fact["kind"] == "external-client"]
    seen = set()
    dependencies = []

    for fact in dependency_facts:
        raw = fact.get("raw_evidence") or {}
        name = str(raw.get("name") or raw.get("target") or raw.get("technology") or fact["id"])
        technology = str(raw.get("technology") or raw.get("target") or "unknown")
        concept = classify_dependency_concept(technology + " " + name)
        key = (name.lower(), technology.lower(), concept)
        if key in seen:
            continue
        seen.add(key)
        resilience = {
            "timeout": coerce_bool(raw.get("timeout", False)),
            "retry": coerce_bool(raw.get("retry", False)),
            "circuit_breaker": coerce_bool(raw.get("circuit_breaker", False)),
            "fallback": raw.get("fallback") if raw.get("fallback") is not None else None,
        }
        missing = [name for name in ("timeout", "retry", "circuit_breaker") if not resilience.get(name)]
        dependency = (
            {
                "id": slugify(name),
                "name": name,
                "concept": concept,
                "technology": technology,
                "components": [str(item) for item in fact.get("relationships", {}).get("component_ids") or [] if item],
                "purpose": str(raw.get("purpose") or fact.get("summary") or "dependency"),
                "criticality": str(raw.get("criticality") or "important"),
                "resilience": resilience,
                "health": {
                    "failure_modes": [
                        {
                            "id": f"{slugify(name)}-availability",
                            "trigger": f"{name} becomes slow or unavailable",
                            "impact": f"Features that depend on {name} may degrade.",
                            "signals": [f"missing-resilience:{item}" for item in missing],
                            "gaps": [f"missing-{item}" for item in missing],
                            "recovery": ["Add timeout, retry, and circuit-breaker where appropriate."],
                            "severity": "medium",
                            "grounded_in": [source_line(item) for item in fact.get("source_files", []) if item],
                        }
                    ] if missing else [],
                    "gaps": [f"missing-{item}" for item in missing],
                },
            }
        )
        if joern:
            components_set = set(dependency["components"])
            grounded = set()
            touch_count = 0
            for touch in joern.get("data_touches", []):
                touch_raw = touch.get("raw_evidence") or {}
                target_parts = [
                    str(touch_raw.get("target_name") or ""),
                    str(touch_raw.get("target_full_name") or ""),
                    str(touch_raw.get("target_code") or ""),
                ]
                if not any(symbols_overlap((name, technology), part) for part in target_parts if part):
                    continue
                touch_count += 1
                components_set.update(str(item) for item in touch.get("relationships", {}).get("component_ids") or [] if item)
                owner_file = str(touch_raw.get("owner_file") or "")
                line_number = int(touch_raw.get("line_number", -1) or -1)
                if owner_file:
                    grounded.add(source_line(f"{owner_file}:{line_number}" if line_number > 0 else owner_file))
            dependency["components"] = sorted(components_set)
            if touch_count >= 3 and dependency.get("criticality") == "important":
                dependency["criticality"] = "critical"
            if grounded and dependency.get("health", {}).get("failure_modes"):
                for item in dependency["health"]["failure_modes"]:
                    item["grounded_in"] = unique_strings(list(item.get("grounded_in") or []) + sorted(grounded))
        dependencies.append(dependency)

    return dependencies


def build_components_and_groups(facts: list[dict[str, Any]], joern: dict[str, Any] | None = None) -> tuple[list[dict[str, Any]], list[str]]:
    buckets: dict[str, dict[str, Any]] = {}
    for fact in facts:
        for component_id in fact.get("relationships", {}).get("component_ids", []) or []:
            bucket = buckets.setdefault(
                component_id,
                {
                    "id": component_id,
                    "name": component_id.replace("-", " ").title(),
                    "modules": set(),
                    "patterns": set(),
                    "depends_on": set(),
                    "type": "library",
                    "health_failure_modes": [],
                    "health_gaps": set(),
                },
            )
            for source in fact.get("source_files", []):
                bucket["modules"].add(source_path(source))
            if fact["kind"] == "route":
                bucket["type"] = "api"
            elif fact["kind"] == "job":
                bucket["type"] = "worker"
            elif fact["kind"] == "external-client" and bucket["type"] == "library":
                bucket["type"] = "service"
            if fact["kind"] in {"auth-surface", "config-source"}:
                bucket["patterns"].add(fact["kind"])
            raw = fact.get("raw_evidence") or {}
            target = str(raw.get("to") or "").strip()
            if target and "/" not in target and "." not in target:
                bucket["depends_on"].add(slugify(target))
            if fact["kind"] == "route":
                bucket["health_failure_modes"].append(
                    {
                        "id": f"{component_id}-request-path",
                        "trigger": "Request handling degrades or fails on this component.",
                        "impact": "User-facing API behavior becomes slow or error-prone.",
                        "signals": ["request.rate", "request.error_rate", "request.latency"],
                        "gaps": [],
                        "recovery": [],
                        "severity": "low",
                        "grounded_in": [source_line(item) for item in fact.get("source_files", []) if item],
                    }
                )
            if fact["kind"] == "job":
                bucket["health_failure_modes"].append(
                    {
                        "id": f"{component_id}-job-execution",
                        "trigger": "Scheduled or background work fails, stalls, or slows down.",
                        "impact": "Background processing becomes unreliable or delayed.",
                        "signals": ["job.run_rate", "job.failure_rate", "job.duration"],
                        "gaps": [],
                        "recovery": [],
                        "severity": "low",
                        "grounded_in": [source_line(item) for item in fact.get("source_files", []) if item],
                    }
                )

    for fact in facts:
        if fact["kind"] != "state-store":
            continue
        raw = fact.get("raw_evidence") or {}
        strategy = str(raw.get("strategy") or raw.get("concurrency_strategy") or "none")
        if strategy != "none":
            continue
        component_ids = fact.get("relationships", {}).get("component_ids") or []
        for component_id in component_ids:
            bucket = buckets.get(component_id)
            if not bucket:
                continue
            bucket["health_failure_modes"].append(
                {
                    "id": f"{component_id}-state-consistency",
                    "trigger": f"{raw.get('technology') or fact.get('summary') or 'state store'} writes conflict without explicit concurrency handling",
                    "impact": "State consistency may degrade under concurrent writes.",
                    "signals": ["missing-concurrency-strategy"],
                    "gaps": ["missing-concurrency-strategy"],
                    "recovery": ["Add an explicit concurrency strategy where concurrent writes are expected."],
                    "severity": "low",
                    "grounded_in": [source_line(item) for item in fact.get("source_files", []) if item],
                }
            )
            bucket["health_gaps"].add("missing-concurrency-strategy")

    if joern:
        component_ids = set(buckets.keys())
        component_signals = {
            component_id: symbol_variants(
                component_id,
                bucket.get("name", ""),
                *[Path(module).stem for module in bucket.get("modules", set()) if module],
            )
            for component_id, bucket in buckets.items()
        }
        for fact in joern.get("call_edges", []):
            raw = fact.get("raw_evidence") or {}
            caller_components = [str(item) for item in fact.get("relationships", {}).get("component_ids") or [] if item]
            callee_hints = symbol_variants(
                str(raw.get("callee_name") or ""),
                str(raw.get("callee_full_name") or ""),
            )
            if not caller_components or not callee_hints:
                continue
            inferred_targets = {
                component_id
                for component_id in component_ids
                if component_id not in caller_components and component_signals.get(component_id, set()) & callee_hints
            }
            for caller_component in caller_components:
                bucket = buckets.get(caller_component)
                if not bucket:
                    continue
                for target in inferred_targets:
                    bucket["depends_on"].add(target)

    components = []
    groups_map: dict[str, list[str]] = {}
    for component_id, bucket in sorted(buckets.items()):
        module_roots = {
            str(module).split("/", 1)[0]
            for module in bucket.get("modules", set())
            if module and "/" in str(module)
        }
        if len(module_roots) == 1:
            group = next(iter(module_roots))
        elif len(module_roots) > 1:
            preferred = [name for name in ("agents", "shared", "lib", "services", "apps") if name in module_roots]
            group = preferred[0] if preferred else sorted(module_roots)[0]
        else:
            group = component_id.split("-", 1)[0] if "-" in component_id else "core"
        groups_map.setdefault(group, []).append(component_id)
        components.append(
            {
                "id": component_id,
                "name": bucket["name"],
                "description": f"Derived component for {component_id}.",
                "type": bucket["type"],
                "parent": None,
                "modules": sorted(bucket["modules"]),
                "depends_on": sorted(dep for dep in bucket["depends_on"] if dep in buckets and dep != component_id),
                "abstraction": [],
                "patterns": sorted(bucket["patterns"]),
                "health": {
                    "failure_modes": merge_failure_modes(bucket["health_failure_modes"]),
                    "gaps": sorted(bucket["health_gaps"]),
                },
                "deployment": {"namespace": "", "kind": "", "replicas": "", "node": ""},
                "children": [],
            }
        )
    existing_ids = {component["id"] for component in components}
    root_ids: list[str] = []
    for group_id, component_ids in sorted(groups_map.items()):
        root_id = group_id if group_id not in existing_ids else f"{group_id}-root"
        root_ids.append(root_id)
        existing_ids.add(root_id)
        components.append(
            {
                "id": root_id,
                "name": group_id.replace("-", " ").title(),
                "description": f"Derived top-level component for the {group_id} architecture slice.",
                "type": "service",
                "parent": None,
                "modules": [],
                "depends_on": [],
                "abstraction": [],
                "patterns": [],
                "health": {"failure_modes": [], "gaps": []},
                "deployment": {"namespace": "", "kind": "", "replicas": "", "node": ""},
                "children": sorted(component_ids),
            }
        )
        for component in components:
            if component["id"] in component_ids:
                component["parent"] = root_id
    return components, root_ids


def build_events(facts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    event_facts = [fact for fact in facts if fact["kind"] == "event"]
    events = []
    for fact in event_facts:
        raw = fact.get("raw_evidence") or {}
        components = fact.get("relationships", {}).get("component_ids") or []
        producer = components[0] if components else "unknown"
        events.append(
            {
                "id": slugify(fact["id"]),
                "type": str(raw.get("event_type") or "signal"),
                "name": str(raw.get("topic") or raw.get("event_type") or fact["summary"]),
                "producer": producer,
                "consumers": [],
                "data": str(raw.get("payload") or ""),
            }
        )
    return events


def build_joern_indexes(facts: list[dict[str, Any]]) -> dict[str, Any]:
    call_edges = [fact for fact in facts if fact["kind"] == "call-edge"]
    data_touches = [fact for fact in facts if fact["kind"] == "data-touch"]
    execution_slices = [fact for fact in facts if fact["kind"] == "execution-slice"]

    touches_by_owner: dict[str, list[dict[str, Any]]] = {}
    slices_by_owner: dict[str, list[dict[str, Any]]] = {}
    edges_by_caller: dict[str, list[dict[str, Any]]] = {}

    for fact in data_touches:
        raw = fact.get("raw_evidence") or {}
        keys = symbol_variants(
            str(raw.get("owner_name") or ""),
            str(raw.get("owner_full_name") or ""),
        )
        for key in keys:
            touches_by_owner.setdefault(key, []).append(fact)

    for fact in execution_slices:
        raw = fact.get("raw_evidence") or {}
        keys = symbol_variants(
            str(raw.get("slice_name") or ""),
            str(raw.get("slice_full_name") or ""),
        )
        for key in keys:
            slices_by_owner.setdefault(key, []).append(fact)

    for fact in call_edges:
        raw = fact.get("raw_evidence") or {}
        keys = symbol_variants(
            str(raw.get("caller_name") or ""),
            str(raw.get("caller_full_name") or ""),
        )
        for key in keys:
            edges_by_caller.setdefault(key, []).append(fact)

    return {
        "call_edges": call_edges,
        "data_touches": data_touches,
        "execution_slices": execution_slices,
        "touches_by_owner": touches_by_owner,
        "slices_by_owner": slices_by_owner,
        "edges_by_caller": edges_by_caller,
    }


def facts_for_owner(index: dict[str, list[dict[str, Any]]], *symbols: str) -> list[dict[str, Any]]:
    matched: list[dict[str, Any]] = []
    seen: set[str] = set()
    for key in symbol_variants(*symbols):
        for fact in index.get(key, []):
            fact_id = str(fact.get("id") or "")
            if fact_id and fact_id not in seen:
                seen.add(fact_id)
                matched.append(fact)
    return matched


def component_for_path(path: str, components: list[dict[str, Any]]) -> str:
    src = source_path(path)
    for component in components:
        for module in component.get("modules") or []:
            if src == module or src.startswith(f"{module}/"):
                return str(component.get("id") or "")
    return ""


def component_symbol_index(components: list[dict[str, Any]]) -> dict[str, set[str]]:
    index: dict[str, set[str]] = {}
    for component in components:
        component_id = str(component.get("id") or "")
        if not component_id:
            continue
        values = [component_id, str(component.get("name") or "")]
        values.extend(Path(str(module)).stem for module in component.get("modules") or [] if module)
        index[component_id] = symbol_variants(*values)
    return index


def build_flows(
    facts: list[dict[str, Any]],
    components: list[dict[str, Any]] | None = None,
    state: list[dict[str, Any]] | None = None,
    external_dependencies: list[dict[str, Any]] | None = None,
    joern: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    candidates: list[tuple[int, dict[str, Any]]] = []
    components = components or []
    state = state or []
    external_dependencies = external_dependencies or []
    component_symbols = component_symbol_index(components)
    used_slice_ids: set[str] = set()

    def best_slice_for_symbols(*symbols: str) -> dict[str, Any] | None:
        if not joern:
            return None
        slice_facts = facts_for_owner(joern.get("slices_by_owner", {}), *symbols)
        if not slice_facts:
            return None
        return max(slice_facts, key=lambda item: len(((item.get("raw_evidence") or {}).get("steps") or [])))

    def touch_facts_for_symbols(*symbols: str) -> list[dict[str, Any]]:
        if not joern:
            return []
        return facts_for_owner(joern.get("touches_by_owner", {}), *symbols)

    def edge_facts_for_symbols(*symbols: str) -> list[dict[str, Any]]:
        if not joern:
            return []
        return facts_for_owner(joern.get("edges_by_caller", {}), *symbols)

    def steps_from_slice(slice_fact: dict[str, Any], base_component: str) -> tuple[list[dict[str, Any]], list[str], set[str]]:
        raw = slice_fact.get("raw_evidence") or {}
        slice_file = str(raw.get("slice_file") or "")
        component = component_for_path(slice_file, components) or base_component
        steps: list[dict[str, Any]] = []
        grounded: list[str] = []
        touched_components: set[str] = {component} if component else set()
        for step in raw.get("steps") or []:
            callee_full_name = str(step.get("callee_full_name") or "")
            callee_name = str(step.get("callee_name") or "")
            line_number = int(step.get("line_number", -1) or -1)
            to_component = ""
            for item in components:
                component_id = str(item.get("id") or "")
                if component_id and component_id != component and symbols_overlap({component_id}, (callee_full_name, callee_name)):
                    to_component = component_id
                    touched_components.add(component_id)
                    break
            steps.append(
                {
                    "component": component,
                    "action": str(step.get("call_code") or callee_name or callee_full_name or "call"),
                    "to": to_component,
                    "technology": "",
                }
            )
            if slice_file:
                grounded.append(source_line(f"{slice_file}:{line_number}" if line_number > 0 else slice_file))
        return steps, grounded, touched_components

    def steps_from_edges(edge_facts: list[dict[str, Any]], base_component: str) -> tuple[list[dict[str, Any]], list[str], set[str]]:
        steps: list[dict[str, Any]] = []
        grounded: list[str] = []
        touched_components: set[str] = {base_component} if base_component else set()
        seen_pairs: set[tuple[str, str, str]] = set()
        for fact in edge_facts[:12]:
            raw = fact.get("raw_evidence") or {}
            caller_file = str(raw.get("caller_file") or raw.get("source_file") or "")
            line_number = int(raw.get("line_number", -1) or -1)
            component = component_for_path(caller_file, components) or base_component
            callee_hints = symbol_variants(
                str(raw.get("callee_name") or ""),
                str(raw.get("callee_full_name") or ""),
            )
            to_component = next(
                (
                    component_id
                    for component_id, signals in component_symbols.items()
                    if component_id != component and signals & callee_hints
                ),
                "",
            )
            pair = (component, to_component, str(raw.get("call_code") or raw.get("callee_name") or ""))
            if pair in seen_pairs:
                continue
            seen_pairs.add(pair)
            if to_component:
                touched_components.add(to_component)
            steps.append(
                {
                    "component": component,
                    "action": str(raw.get("call_code") or raw.get("callee_name") or raw.get("callee_full_name") or "call"),
                    "to": to_component,
                    "technology": "",
                }
            )
            if caller_file:
                grounded.append(source_line(f"{caller_file}:{line_number}" if line_number > 0 else caller_file))
        return steps, grounded, touched_components

    def apply_touches(flow: dict[str, Any], touch_facts: list[dict[str, Any]], base_component: str) -> tuple[int, int]:
        steps = list(flow.get("steps") or [])
        grounded = set(flow.get("grounded_in") or [])
        state_hits = 0
        dependency_hits = 0
        for touch in touch_facts[:6]:
            touch_raw = touch.get("raw_evidence") or {}
            owner_file = str(touch_raw.get("owner_file") or "")
            line_number = int(touch_raw.get("line_number", -1) or -1)
            component = component_for_path(owner_file, components) or base_component
            target_name = str(touch_raw.get("target_name") or touch_raw.get("target_full_name") or "")
            target_code = str(touch_raw.get("target_code") or "")
            touch_kind = str(touch_raw.get("touch_kind") or "")
            for entry in state:
                if symbols_overlap((entry.get("technology", ""), entry.get("stores", "")), (target_name, target_code)):
                    steps.append(
                        {
                            "component": component,
                            "action": f"{touch_kind} state",
                            "to": str(entry.get("component") or ""),
                            "data": str(entry.get("stores") or entry.get("technology") or ""),
                            "technology": str(entry.get("technology") or ""),
                        }
                    )
                    state_hits += 1
                    if owner_file:
                        grounded.add(source_line(f"{owner_file}:{line_number}" if line_number > 0 else owner_file))
                    break
            else:
                for dependency in external_dependencies:
                    if symbols_overlap((dependency.get("name", ""), dependency.get("technology", "")), (target_name, target_code)):
                        dependency_components = [str(item) for item in dependency.get("components") or [] if item]
                        to_component = next((item for item in dependency_components if item != component), "")
                        steps.append(
                            {
                                "component": component,
                                "action": f"{touch_kind} dependency",
                                "to": to_component,
                                "technology": str(dependency.get("technology") or ""),
                                "data": target_name,
                            }
                        )
                        dependency_hits += 1
                        if owner_file:
                            grounded.add(source_line(f"{owner_file}:{line_number}" if line_number > 0 else owner_file))
                        break
        flow["steps"] = steps[:12]
        flow["grounded_in"] = sorted(grounded)
        return state_hits, dependency_hits

    def score_candidate(base: int, flow: dict[str, Any], *, slice_step_count: int = 0, component_span: int = 0, state_hits: int = 0, dependency_hits: int = 0, edge_count: int = 0) -> int:
        return base + min(slice_step_count, 8) * 3 + min(component_span, 4) * 5 + state_hits * 4 + dependency_hits * 4 + min(edge_count, 6)

    def register_candidate(base_score: int, flow: dict[str, Any], *, slice_fact: dict[str, Any] | None, touch_facts: list[dict[str, Any]], edge_facts: list[dict[str, Any]], base_component: str) -> None:
        slice_step_count = 0
        component_span = 1
        if slice_fact:
            used_slice_ids.add(str(slice_fact.get("id") or ""))
            slice_steps, slice_grounded, touched_components = steps_from_slice(slice_fact, base_component)
            if slice_steps:
                flow["steps"] = slice_steps
                flow["grounded_in"] = sorted(set(flow.get("grounded_in") or []) | set(slice_grounded))
            slice_step_count = len(slice_steps)
            component_span = max(1, len(touched_components))
        elif edge_facts:
            edge_steps, edge_grounded, touched_components = steps_from_edges(edge_facts, base_component)
            if edge_steps:
                flow["steps"] = edge_steps
                flow["grounded_in"] = sorted(set(flow.get("grounded_in") or []) | set(edge_grounded))
            slice_step_count = len(edge_steps)
            component_span = max(1, len(touched_components))
        state_hits, dependency_hits = apply_touches(flow, touch_facts, base_component)
        if edge_facts and len(edge_facts) > 3 and flow.get("health", {}).get("failure_modes"):
            flow["health"]["failure_modes"][0]["signals"] = unique_strings(
                list(flow["health"]["failure_modes"][0].get("signals") or []) + ["call.path.depth"]
            )
        flow["business_metrics"] = derive_flow_business_metrics(flow)
        candidates.append(
            (
                score_candidate(
                    base_score,
                    flow,
                    slice_step_count=slice_step_count,
                    component_span=component_span,
                    state_hits=state_hits,
                    dependency_hits=dependency_hits,
                    edge_count=len(edge_facts),
                ),
                flow,
            )
        )

    route_kinds = {"route", "graphql-operation", "grpc-service", "websocket-channel"}
    for fact in facts:
        if fact["kind"] not in route_kinds:
            continue
        raw = fact.get("raw_evidence") or {}
        component_ids = [str(item) for item in fact.get("relationships", {}).get("component_ids") or [] if item]
        if not component_ids:
            continue
        grounded = should_keep_grounded_sources(fact.get("source_files", []))
        if not grounded:
            continue
        component = component_ids[0]
        method = str(raw.get("method") or raw.get("http_method") or fact["kind"]).upper()
        path = str(raw.get("path") or raw.get("route") or raw.get("endpoint") or raw.get("name") or fact["id"])
        if is_internal_route_path(path):
            continue
        flow_id = slugify(f"{component}-{method}-{path}")
        flow = {
            "id": flow_id,
            "type": "control",
            "name": f"{method} {path}",
            "description": f"Request flow handled by {component}.",
            "trigger": f"{method} {path}",
            "actors": ["api-client"],
            "grounded_in": grounded,
            "health": {
                "failure_modes": [
                    {
                        "id": f"{flow_id}-request-failure",
                        "trigger": "Request handling slows down or fails.",
                        "impact": "Clients experience latency, errors, or incomplete responses.",
                        "signals": ["request.error_rate", "request.latency"],
                        "gaps": [],
                        "recovery": [],
                        "severity": "medium",
                        "grounded_in": grounded,
                    }
                ],
                "gaps": [],
            },
            "business_metrics": [],
            "steps": [
                {
                    "component": component,
                    "action": f"handle {method} {path}",
                    "to": "",
                }
            ],
        }
        symbols = [str(raw.get("handler") or ""), path, str(flow.get("name") or "")]
        register_candidate(
            100,
            flow,
            slice_fact=best_slice_for_symbols(*symbols),
            touch_facts=touch_facts_for_symbols(*symbols),
            edge_facts=edge_facts_for_symbols(*symbols),
            base_component=component,
        )

    for fact in facts:
        if fact["kind"] not in {"job", "handler", "event"}:
            continue
        raw = fact.get("raw_evidence") or {}
        component_ids = [str(item) for item in fact.get("relationships", {}).get("component_ids") or [] if item]
        if not component_ids:
            continue
        grounded = should_keep_grounded_sources(fact.get("source_files", []))
        if not grounded:
            continue
        component = component_ids[0]
        name = str(raw.get("name") or raw.get("job") or raw.get("handler") or raw.get("topic") or raw.get("event_type") or fact["summary"] or fact["id"])
        if name.lower().startswith("detected job type"):
            continue
        trigger = str(raw.get("transport") or raw.get("schedule") or raw.get("event_type") or "background")
        flow_id = slugify(f"{component}-{trigger}-{name}")
        if fact["kind"] == "job":
            actors = ["scheduler"]
            base_score = 75
        elif fact["kind"] == "event":
            actors = ["event-source"]
            base_score = 65
        else:
            actors = ["event-source"]
            base_score = 70
        flow = {
            "id": flow_id,
            "type": "control",
            "name": name,
            "description": f"Background or workflow execution through {component}.",
            "trigger": trigger,
            "actors": actors,
            "grounded_in": grounded,
            "health": {
                "failure_modes": [
                    {
                        "id": f"{flow_id}-execution-failure",
                        "trigger": "Background execution stalls, retries excessively, or fails.",
                        "impact": "Deferred work becomes delayed or incomplete.",
                        "signals": ["job.failure_rate", "job.duration"],
                        "gaps": [],
                        "recovery": [],
                        "severity": "low",
                        "grounded_in": grounded,
                    }
                ],
                "gaps": [],
            },
            "business_metrics": [],
            "steps": [
                {
                    "component": component,
                    "action": f"execute {name}",
                    "to": "",
                }
            ],
        }
        symbols = [str(raw.get("name") or ""), str(raw.get("handler") or ""), str(raw.get("topic") or ""), name, trigger]
        register_candidate(
            base_score,
            flow,
            slice_fact=best_slice_for_symbols(*symbols),
            touch_facts=touch_facts_for_symbols(*symbols),
            edge_facts=edge_facts_for_symbols(*symbols),
            base_component=component,
        )

    for slice_fact in (joern or {}).get("execution_slices", []):
        slice_id = str(slice_fact.get("id") or "")
        if slice_id and slice_id in used_slice_ids:
            continue
        raw = slice_fact.get("raw_evidence") or {}
        slice_file = str(raw.get("slice_file") or "")
        grounded = should_keep_grounded_sources([source_line(f"{slice_file}:{int(raw.get('slice_line', -1) or -1)}" if int(raw.get('slice_line', -1) or -1) > 0 else slice_file)])
        if not grounded:
            continue
        base_component = component_for_path(slice_file, components)
        steps = raw.get("steps") or []
        if not steps or len(steps) < 2:
            continue
        slice_name = str(raw.get("slice_name") or raw.get("slice_full_name") or "runtime-path")
        flow_id = slugify(f"{base_component or 'runtime'}-{slice_name}")
        flow = {
            "id": flow_id,
            "type": "control",
            "name": slice_name,
            "description": f"Slice-derived runtime path through {base_component or 'the system'}.",
            "trigger": "slice-derived",
            "actors": ["service"],
            "grounded_in": grounded,
            "health": {
                "failure_modes": [
                    {
                        "id": f"{flow_id}-execution-path",
                        "trigger": "A key runtime path degrades or breaks.",
                        "impact": "A meaningful code path may fail, stall, or misbehave.",
                        "signals": ["call.path.depth"],
                        "gaps": [],
                        "recovery": [],
                        "severity": "low",
                        "grounded_in": grounded,
                    }
                ],
                "gaps": [],
            },
            "business_metrics": [],
            "steps": [],
        }
        register_candidate(
            55,
            flow,
            slice_fact=slice_fact,
            touch_facts=touch_facts_for_symbols(slice_name, str(raw.get("slice_full_name") or "")),
            edge_facts=edge_facts_for_symbols(slice_name, str(raw.get("slice_full_name") or "")),
            base_component=base_component,
        )

    flows: list[dict[str, Any]] = []
    seen: set[str] = set()
    for _, flow in sorted(candidates, key=lambda item: (item[0], len(item[1].get("steps") or []), len(item[1].get("grounded_in") or [])), reverse=True):
        flow_id = str(flow.get("id") or "")
        if not flow_id or flow_id in seen:
            continue
        seen.add(flow_id)
        flows.append(flow)

    for flow in flows:
        normalize_health_block(flow)
    return flows[:40]


def build_actors(facts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    actors: dict[str, dict[str, Any]] = {}
    for fact in facts:
        if fact["kind"] == "route":
            actors.setdefault("api-client", {"id": "api-client", "type": "user", "description": "Calls detected API routes."})
        elif fact["kind"] == "job":
            actors.setdefault("scheduler", {"id": "scheduler", "type": "cron", "description": "Triggers detected background jobs."})
        elif fact["kind"] == "event":
            actors.setdefault("event-source", {"id": "event-source", "type": "service", "description": "Produces or consumes detected events."})
    return list(actors.values())


def build_module_graph(facts: list[dict[str, Any]]) -> dict[str, Any]:
    import_edges = [fact for fact in facts if fact["kind"] == "import-edge"]
    hot_files = [fact for fact in facts if fact["kind"] == "hot-file"]
    modules: dict[str, dict[str, Any]] = {}
    fan_in: Counter[str] = Counter()
    fan_out: Counter[str] = Counter()

    def ensure_module(path: str) -> dict[str, Any]:
        module = modules.setdefault(
            path,
            {
                "id": path,
                "imports": [],
                "imported_by": [],
                "role": "standard",
            },
        )
        return module

    for fact in import_edges:
        raw = fact.get("raw_evidence") or {}
        src = str(raw.get("from") or raw.get("source") or "").strip()
        dst = str(raw.get("to") or raw.get("target") or "").strip()
        if not src or not dst:
            continue
        ensure_module(src)["imports"].append(dst)
        ensure_module(dst)["imported_by"].append(src)
        fan_out[src] += 1
        fan_in[dst] += 1

    for path in unique_strings([str(raw.get("path") or raw.get("module") or "") for fact in hot_files for raw in [fact.get("raw_evidence") or {}] if raw]):
        if path:
            ensure_module(path)

    for path, module in modules.items():
        module["imports"] = unique_strings(module["imports"])
        module["imported_by"] = unique_strings(module["imported_by"])

    if modules:
        hubs = set()
        ranked = sorted(
            modules.keys(),
            key=lambda path: (fan_in[path], fan_out[path], path),
            reverse=True,
        )
        for path in ranked[: min(3, len(ranked))]:
            hubs.add(path)
        for path, module in modules.items():
            if path in hubs:
                module["role"] = "hub"
            elif not module["imports"] and module["imported_by"]:
                module["role"] = "leaf"
            elif module["imports"] and module["imported_by"]:
                module["role"] = "shared"
    else:
        ranked = []
        hubs = set()

    cycles = find_cycles(modules)

    risks = {
        "hardcoded_endpoints": [
            fact["source_files"][0]
            for fact in facts
            if fact["kind"] == "external-client"
            and str((fact.get("raw_evidence") or {}).get("technology", "")).startswith("http")
            and coerce_bool((fact.get("raw_evidence") or {}).get("hardcoded", False))
        ],
        "missing_resilience": [
            {
                "file": fact["source_files"][0] if fact.get("source_files") else "",
                "service_type": str((fact.get("raw_evidence") or {}).get("technology") or "unknown"),
                "missing": [
                    name
                    for name, enabled in [
                        ("timeout", coerce_bool((fact.get("raw_evidence") or {}).get("timeout", False))),
                        ("retry", coerce_bool((fact.get("raw_evidence") or {}).get("retry", False))),
                        ("circuit_breaker", coerce_bool((fact.get("raw_evidence") or {}).get("circuit_breaker", False))),
                    ]
                    if not enabled
                ],
            }
            for fact in facts
            if fact["kind"] == "external-client"
        ],
        "unversioned_deps": [],
    }

    return {
        "modules": list(modules.values()),
        "circular_dependencies": cycles,
        "hub_modules": ranked[: min(3, len(ranked))] if modules else [],
        "infrastructure": [],
        "inter_service": [],
        "ci_cd": [],
        "iac": [],
        "risks": risks,
    }


def find_cycles(modules: dict[str, dict[str, Any]]) -> list[dict[str, list[str]]]:
    graph = {path: set(module["imports"]) for path, module in modules.items()}
    seen: set[str] = set()
    stack: list[str] = []
    cycles: list[dict[str, list[str]]] = []
    cycle_set: set[tuple[str, ...]] = set()

    def visit(node: str) -> None:
        if node in stack:
            cycle = stack[stack.index(node):] + [node]
            canonical = tuple(sorted(cycle))
            if canonical not in cycle_set:
                cycle_set.add(canonical)
                cycles.append({"cycle": cycle})
            return
        if node in seen:
            return
        seen.add(node)
        stack.append(node)
        for neighbor in graph.get(node, set()):
            if neighbor in graph:
                visit(neighbor)
        stack.pop()

    for node in graph:
        visit(node)
    return cycles


def build_stack(facts: list[dict[str, Any]]) -> dict[str, Any]:
    frameworks, language_hints = build_frameworks(facts)
    languages = unique_strings(
        [lang for lang in language_hints if lang]
        + [lang for fact in facts for lang in fact.get("framework_context", []) if lang]
    )
    if not languages:
        inferred = [classify_language(source) for fact in facts for source in fact.get("source_files", [])]
        languages = unique_strings([lang for lang in inferred if lang])

    runtime = "facts-derived runtime"
    if len(languages) == 1:
        runtime = f"{languages[0]} application"
    elif len(languages) > 1:
        runtime = f"mixed runtime ({', '.join(languages)})"

    return {
        "languages": languages,
        "frameworks": frameworks,
        "runtime": runtime,
    }


def selected_patterns(patterns: list[dict[str, Any]]) -> list[dict[str, Any]]:
    selected: list[dict[str, Any]] = []
    for pattern in patterns:
        verdict = pattern.get("verdict") or {}
        verdict_value = str(verdict.get("verdict") or "").strip().lower()
        if verdict_value in {"confirmed", "candidate"} or not verdict_value:
            selected.append(pattern)
    return selected


def pattern_grounding(pattern: dict[str, Any]) -> list[str]:
    verdict = pattern.get("verdict") or {}
    grounded = verdict.get("grounded_in") or []
    if grounded:
        return [source_line(str(item)) for item in grounded if item]
    evidence = pattern.get("evidence") or {}
    return [source_line(str(item)) for item in evidence.get("files") or [] if item]


def monitoring_signal_names(monitoring: dict[str, Any]) -> list[str]:
    names: list[str] = []
    for item in monitoring.get("health_signals") or []:
        if isinstance(item, dict) and item.get("name"):
            names.append(str(item["name"]))
    return names


def append_concept_health(
    target: dict[str, Any],
    target_kind: str,
    concept_id: str,
    monitoring: dict[str, Any],
    grounded_in: list[str],
) -> None:
    health = target.setdefault("health", {})
    existing_gaps = health.get("gaps") or []
    existing_failure_modes = health.get("failure_modes") or []
    health["gaps"] = unique_strings(existing_gaps + [str(item) for item in monitoring.get("gaps") or [] if item])

    failure_mode_id = f"{target.get('id', 'entity')}-{slugify(concept_id)}-runtime"
    if not any(isinstance(item, dict) and item.get("id") == failure_mode_id for item in existing_failure_modes):
        signals = monitoring_signal_names(monitoring)
        gaps = [str(item) for item in monitoring.get("gaps") or [] if item]
        if signals or gaps:
            existing_failure_modes.append(
                {
                    "id": failure_mode_id,
                    "trigger": f"{concept_id} runtime path degrades for this {target_kind}.",
                    "impact": f"{target_kind.replace('-', ' ').title()} behavior may become slow, error-prone, or unavailable.",
                    "signals": signals,
                    "gaps": gaps,
                    "recovery": [],
                    "severity": "medium" if target_kind == "external-dependency" else "low",
                    "grounded_in": grounded_in,
                }
            )
    health["failure_modes"] = merge_failure_modes(existing_failure_modes)


def attach_concept_monitoring(
    components: list[dict[str, Any]],
    external_dependencies: list[dict[str, Any]],
    flows: list[dict[str, Any]],
    patterns: list[dict[str, Any]],
    monitoring_index: dict[str, dict[str, Any]],
) -> None:
    component_map = {component.get("id"): component for component in components if component.get("id")}

    for pattern in selected_patterns(patterns):
        concept_id = str(pattern.get("id") or "")
        monitoring = monitoring_index.get(concept_id)
        if not monitoring:
            continue
        applies_to = {str(item) for item in monitoring.get("applies_to") or [] if item}
        component_ids = [str(item) for item in pattern.get("components") or [] if item]
        grounded_in = pattern_grounding(pattern)

        if "component" in applies_to:
            for component_id in component_ids:
                component = component_map.get(component_id)
                if component:
                    append_concept_health(component, "component", concept_id, monitoring, grounded_in)

        if "dependency" in applies_to and component_ids:
            component_set = set(component_ids)
            for dependency in external_dependencies:
                dependency_components = {str(item) for item in dependency.get("components") or [] if item}
                if dependency_components & component_set:
                    append_concept_health(dependency, "external-dependency", concept_id, monitoring, grounded_in)

        if "flow" in applies_to:
            for flow in flows:
                flow_components = {
                    str(step.get("component"))
                    for step in flow.get("steps") or []
                    if isinstance(step, dict) and step.get("component")
                }
                if flow_components & set(component_ids):
                    append_concept_health(flow, "flow", concept_id, monitoring, grounded_in)
                    flow.setdefault("business_metrics", [])
                    for metric in monitoring.get("business_metrics") or []:
                        if not isinstance(metric, dict) or not metric.get("name"):
                            continue
                        candidate = {
                            "name": str(metric["name"]),
                            "description": str(metric.get("description") or ""),
                            "owner": str(flow.get("id") or "flow"),
                            "grounded_in": grounded_in,
                        }
                        if candidate not in flow["business_metrics"]:
                            flow["business_metrics"].append(candidate)
    return None


def build_output(
    project: str,
    facts_root: Path,
    facts_index_path: Path,
    analysis_mode: str,
    purpose: str | None,
    seed_mode: bool = False,
) -> dict[str, Any]:
    index, documents = load_fact_documents(facts_root)
    facts = collect_facts(documents)
    joern = build_joern_indexes(facts)
    detected_patterns = load_detected_patterns(facts)
    monitoring_index = load_monitoring_index()

    components, root_components = build_components_and_groups(facts, joern)
    if seed_mode:
        domain_model = {
            "primary": "software-system",
            "description": "Initial semantic seed synthesized from deterministic facts.",
            "entities": [],
            "relationships": [],
            "bounded_contexts": [],
        }
        state = []
        external_dependencies = []
        module_graph = {"modules": [], "circular_dependencies": [], "hub_modules": [], "infrastructure": [], "inter_service": [], "ci_cd": [], "iac": [], "risks": {"hardcoded_endpoints": [], "missing_resilience": [], "unversioned_deps": []}}
        events = []
        actors = []
        flows = []
    else:
        domain_model = build_domain_model(facts)
        state = build_state_entries(facts, joern)
        external_dependencies = build_external_dependencies(facts, joern)
        module_graph = build_module_graph(facts)
        events = build_events(facts)
        actors = build_actors(facts)
        flows = build_flows(facts, components, state, external_dependencies, joern)
        attach_concept_monitoring(
            components,
            external_dependencies,
            flows,
            detected_patterns,
            monitoring_index,
        )
        for component in components:
            normalize_health_block(component)
        for dependency in external_dependencies:
            normalize_health_block(dependency)
        for flow in flows:
            normalize_health_block(flow)
    if not purpose:
        purpose = f"{project} system synthesized from extracted facts." if project else "System synthesized from extracted facts."

    metadata = {
        "story_ids": [],
        "analyzed_at_sha": index.get("metadata", {}).get("analyzed_at_sha", "") if isinstance(index, dict) else "",
        "analysis_mode": analysis_mode,
        "root_components": root_components,
        "affected_components": unique_strings(
            [component for fact in facts for component in fact.get("relationships", {}).get("component_ids", []) if component]
        ),
        "analysis_root": "",
        "meta_path": "",
        "base_sha": "",
        "base_commit_time": "",
        "flags": {"deterministic_only": False},
        "facts_index": str(facts_index_path),
        "facts_count": len(facts),
        "concept_count": len(detected_patterns),
        "facts_domains": unique_strings([fact.get("domain", "") for fact in facts if fact.get("domain")]),
        "seed_mode": seed_mode,
    }

    concepts = {
        "detected_patterns": [],
        "detected_anti_patterns": [],
        "gaps": [],
    }

    output: dict[str, Any] = {
        "version": "4",
        "generated": date.today().isoformat(),
        "project": project,
        "purpose": purpose,
        "components": components,
        "flows": flows,
        "state": state,
        "external_dependencies": external_dependencies,
        "concepts": concepts,
        "tensions": [],
        "metadata": metadata,
    }
    if domain_model and not seed_mode:
        output["domain_model"] = domain_model
    elif seed_mode:
        output["domain_model"] = domain_model
    if actors:
        output["actors"] = actors
    if events:
        output["events"] = events
    if module_graph and not seed_mode:
        output["module_graph"] = module_graph
    return output


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Synthesize atlas sections from Augur facts")
    parser.add_argument("facts", type=Path, help="Path to facts directory or facts/index.json")
    parser.add_argument("--project", default="", help="Project name to place in the synthesized output")
    parser.add_argument("--purpose", default="", help="Optional explicit purpose override")
    parser.add_argument("--output", type=Path, default=None, help="Write synthesized atlas JSON to this file")
    parser.add_argument("--analysis-mode", default="facts-to-atlas", help="Metadata analysis mode label")
    parser.add_argument("--seed", action="store_true", help="Emit a compact schema-correct semantic seed instead of a broad facts-derived atlas")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    facts_root = args.facts
    if not facts_root.exists():
        print(f"facts path does not exist: {facts_root}", file=sys.stderr)
        return 2

    project = args.project.strip()
    index_path = facts_root / "index.json" if facts_root.is_dir() else facts_root
    if not project and index_path.exists():
        try:
            payload = read_json(index_path)
            if isinstance(payload, dict):
                project = str(payload.get("project") or payload.get("metadata", {}).get("project") or "")
        except Exception:
            project = ""
    if not project:
        project = facts_root.name if facts_root.name != "index.json" else "augur-project"

    output = build_output(
        project,
        facts_root,
        index_path,
        args.analysis_mode,
        args.purpose.strip() or None,
        seed_mode=args.seed,
    )
    text = json.dumps(output, indent=2, sort_keys=False) + "\n"
    if args.output:
        write_json(args.output, output)
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
