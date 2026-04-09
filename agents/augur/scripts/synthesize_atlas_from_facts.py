#!/usr/bin/env python3
"""Synthesize an atlas fragment from Augur facts.

This CLI reads normalized facts from `facts/` and derives the atlas sections
that can be built directly from first-order evidence:

- stack
- domain_model hints
- api_surface
- state
- external_dependencies
- module_graph

It is intentionally conservative. It does not infer concepts or debt, and it
does not try to recreate full architectural narration. That remains the job of
the concept layer and the atlas composer.
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


def coerce_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value != 0
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "y", "on"}
    return bool(value)


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
            primary = "property-graph"
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


def build_state_entries(facts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    state_facts = [fact for fact in facts if fact["kind"] in {"model", "state-store"}]
    entries = []
    for fact in state_facts:
        raw = fact.get("raw_evidence") or {}
        technology = str(raw.get("technology") or raw.get("store") or "unknown")
        concept = classify_store_concept(technology + " " + fact.get("summary", ""))
        component_ids = fact.get("relationships", {}).get("component_ids") or []
        component = component_ids[0] if component_ids else "unknown"
        entries.append(
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
    return entries


def build_external_dependencies(facts: list[dict[str, Any]]) -> list[dict[str, Any]]:
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
        dependencies.append(
            {
                "id": slugify(name),
                "name": name,
                "concept": concept,
                "technology": technology,
                "components": [str(item) for item in fact.get("relationships", {}).get("component_ids") or [] if item],
                "purpose": str(raw.get("purpose") or fact.get("summary") or "dependency"),
                "criticality": str(raw.get("criticality") or "important"),
                "resilience": {
                    "timeout": coerce_bool(raw.get("timeout", False)),
                    "retry": coerce_bool(raw.get("retry", False)),
                    "circuit_breaker": coerce_bool(raw.get("circuit_breaker", False)),
                    "fallback": raw.get("fallback") if raw.get("fallback") is not None else None,
                },
            }
        )

    return dependencies


def build_components_and_groups(facts: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
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

    components = []
    groups_map: dict[str, list[str]] = {}
    for component_id, bucket in sorted(buckets.items()):
        group = component_id.split("-", 1)[0] if "-" in component_id else "core"
        groups_map.setdefault(group, []).append(component_id)
        components.append(
            {
                "id": component_id,
                "name": bucket["name"],
                "description": f"Derived component for {component_id}.",
                "type": bucket["type"],
                "group": group,
                "modules": sorted(bucket["modules"]),
                "depends_on": sorted(dep for dep in bucket["depends_on"] if dep in buckets and dep != component_id),
                "abstraction": [],
                "patterns": sorted(bucket["patterns"]),
                "deployment": {"namespace": "", "kind": "", "replicas": "", "node": ""},
                "children": [],
            }
        )

    groups = [
        {
            "id": group_id,
            "name": group_id.replace("-", " ").title(),
            "description": f"Derived group for {group_id}.",
            "components": sorted(component_ids),
        }
        for group_id, component_ids in sorted(groups_map.items())
    ]
    return components, groups


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


def build_failure_modes(external_dependencies: list[dict[str, Any]], state: list[dict[str, Any]]) -> list[dict[str, Any]]:
    failure_modes = []
    for dep in external_dependencies:
        missing = [name for name in ("timeout", "retry", "circuit_breaker") if not dep["resilience"].get(name)]
        if not missing:
            continue
        failure_modes.append(
            {
                "id": f"{dep['id']}-availability",
                "trigger": f"{dep['name']} becomes slow or unavailable",
                "cascade": [{"component": component, "effect": f"calls to {dep['name']} may fail"} for component in dep.get("components", [])],
                "impact": f"Features that depend on {dep['name']} may degrade.",
                "detection": {
                    "signals": [f"missing-resilience:{name}" for name in missing],
                    "concern": "dependency-availability",
                    "source_pattern": None,
                },
                "recovery": ["Add timeout, retry, and circuit-breaker where appropriate."],
                "severity": "medium",
                "grounded_in": [],
            }
        )
    for entry in state:
        if entry["concurrency"]["strategy"] == "none":
            failure_modes.append(
                {
                    "id": f"{entry['id']}-state-consistency",
                    "trigger": f"{entry['technology']} writes conflict without explicit concurrency handling",
                    "cascade": [{"component": entry["component"], "effect": "state conflicts may go undetected"}],
                    "impact": "State consistency may degrade under concurrent writes.",
                    "detection": {
                        "signals": ["missing-concurrency-strategy"],
                        "concern": "state-consistency",
                        "source_pattern": None,
                    },
                    "recovery": ["Add an explicit concurrency strategy where concurrent writes are expected."],
                    "severity": "low",
                    "grounded_in": entry.get("grounded_in", []),
                }
            )
    return failure_modes


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


def build_output(
    project: str,
    facts_root: Path,
    facts_index_path: Path,
    analysis_mode: str,
    purpose: str | None,
) -> dict[str, Any]:
    index, documents = load_fact_documents(facts_root)
    facts = collect_facts(documents)

    stack = build_stack(facts)
    api_surface, _ = build_routes(facts)
    domain_model = build_domain_model(facts)
    state = build_state_entries(facts)
    external_dependencies = build_external_dependencies(facts)
    module_graph = build_module_graph(facts)
    components, groups = build_components_and_groups(facts)
    events = build_events(facts)
    actors = build_actors(facts)
    failure_modes = build_failure_modes(external_dependencies, state)

    if not purpose:
        if stack["frameworks"]:
            purpose = f"{project} system synthesized from extracted facts."
        else:
            purpose = "System synthesized from extracted facts."

    metadata = {
        "story_ids": [],
        "analyzed_at_sha": index.get("metadata", {}).get("analyzed_at_sha", "") if isinstance(index, dict) else "",
        "analysis_mode": analysis_mode,
        "affected_components": unique_strings(
            [component for fact in facts for component in fact.get("relationships", {}).get("component_ids", []) if component]
        ),
        "flags": {"detect_only": False},
        "facts_index": str(facts_index_path),
        "facts_count": len(facts),
        "facts_domains": unique_strings([fact.get("domain", "") for fact in facts if fact.get("domain")]),
    }

    concepts = {
        "detected_patterns": [],
        "detected_anti_patterns": [],
        "gaps": [],
        "scan_metadata": {
            "catalog_size": {"patterns": 0, "anti_patterns": 0},
            "tools_used": ["facts-synthesis"],
            "categories_scanned": [],
            "facts_index": metadata["facts_index"],
            "fact_domains_used": metadata["facts_domains"],
        },
    }

    debt = {
        "score": 0,
        "grade": "A",
        "grade_capped": False,
        "interpretation": "Facts-derived scaffold. Concept detection has not been run.",
        "by_category": [],
        "violations": [],
        "recommendations": [],
    }

    return {
        "version": "4",
        "generated": date.today().isoformat(),
        "project": project,
        "purpose": purpose,
        "domain_model": domain_model,
        "stack": stack,
        "groups": groups,
        "actors": actors,
        "components": components,
        "flows": [],
        "api_surface": api_surface,
        "state": state,
        "events": events,
        "external_dependencies": external_dependencies,
        "failure_modes": failure_modes,
        "concepts": concepts,
        "module_graph": module_graph,
        "debt": debt,
        "metadata": metadata,
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Synthesize atlas sections from Augur facts")
    parser.add_argument("facts", type=Path, help="Path to facts directory or facts/index.json")
    parser.add_argument("--project", default="", help="Project name to place in the synthesized output")
    parser.add_argument("--purpose", default="", help="Optional explicit purpose override")
    parser.add_argument("--output", type=Path, default=None, help="Write synthesized atlas JSON to this file")
    parser.add_argument("--analysis-mode", default="facts-to-atlas", help="Metadata analysis mode label")
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
    )
    text = json.dumps(output, indent=2, sort_keys=False) + "\n"
    if args.output:
        write_json(args.output, output)
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
