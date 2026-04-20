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
import re


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


def load_optional_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = read_json(path)
    except Exception:
        return {}
    return payload if isinstance(payload, dict) else {}


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


OBSERVABILITY_KEYWORDS = {
    "metric", "metrics", "counter", "histogram", "gauge", "summary",
    "observe", "record", "telemetry", "prometheus", "statsd", "datadog",
    "otel", "opentelemetry", "trace", "tracing", "span", "meter",
}


def metric_tokens(name: str) -> list[str]:
    tokens = [token.lower() for token in re.split(r"[^A-Za-z0-9]+", name or "") if token]
    return [token for token in tokens if len(token) >= 3]


def monitoring_evidence_paths(
    repo_root: Path | None,
    pattern: dict[str, Any],
    component_map: dict[str, dict[str, Any]],
) -> list[Path]:
    candidates: list[Path] = []
    if not repo_root or not repo_root.exists():
        return candidates

    seen: set[Path] = set()

    def add_path(raw: str) -> None:
        base = source_path(raw)
        path = Path(base)
        resolved = path if path.is_absolute() else (repo_root / base)
        if not resolved.exists() or resolved in seen:
            return
        seen.add(resolved)
        candidates.append(resolved)

    for ref in pattern.get("grounded_in") or []:
        add_path(str(ref))
    evidence = pattern.get("evidence") or {}
    for ref in evidence.get("files") or []:
        add_path(str(ref))
    for component_id in pattern.get("components") or []:
        component = component_map.get(str(component_id))
        if not component:
            continue
        for module in component.get("modules") or []:
            add_path(str(module))

    expanded: list[Path] = []
    for path in candidates[:12]:
        if path.is_dir():
            for child in sorted(path.rglob("*")):
                if child.is_file() and child.suffix.lower() in LANGUAGE_BY_SUFFIX:
                    expanded.append(child)
                    if len(expanded) >= 30:
                        break
        elif path.is_file():
            expanded.append(path)
        if len(expanded) >= 30:
            break
    return expanded[:30]


def file_has_metric_evidence(path: Path, metric_name: str) -> bool:
    try:
        text = path.read_text(encoding="utf-8", errors="ignore").lower()
    except OSError:
        return False
    tokens = metric_tokens(metric_name)
    if not tokens:
        return False
    if metric_name.lower() in text:
        return True
    if not any(keyword in text for keyword in OBSERVABILITY_KEYWORDS):
        return False
    token_hits = sum(1 for token in tokens if token in text)
    return token_hits >= max(2, min(3, len(tokens)))


def evaluate_monitoring_expectations(
    repo_root: Path | None,
    pattern: dict[str, Any],
    monitoring: dict[str, Any],
    component_map: dict[str, dict[str, Any]],
) -> tuple[list[str], list[dict[str, Any]], list[str]]:
    evidence_files = monitoring_evidence_paths(repo_root, pattern, component_map)
    observed_signals: list[str] = []
    observed_metrics: list[dict[str, Any]] = []
    missing_gaps: list[str] = []

    for item in monitoring.get("health_signals") or []:
        if not isinstance(item, dict) or not item.get("name"):
            continue
        name = str(item["name"])
        if any(file_has_metric_evidence(path, name) for path in evidence_files):
            observed_signals.append(name)
        else:
            missing_gaps.append(
                f"No clear repo evidence of monitoring for expected signal `{name}` implied by concept `{pattern.get('id')}`."
            )

    for item in monitoring.get("business_metrics") or []:
        if not isinstance(item, dict) or not item.get("name"):
            continue
        name = str(item["name"])
        if any(file_has_metric_evidence(path, name) for path in evidence_files):
            observed_metrics.append(item)
        else:
            missing_gaps.append(
                f"No clear repo evidence of monitoring for expected business metric `{name}` implied by concept `{pattern.get('id')}`."
            )

    return observed_signals, observed_metrics, missing_gaps


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


def titleize_slug(value: str) -> str:
    return " ".join(part.capitalize() for part in re.split(r"[-_]+", value or "") if part)


def classify_gap_kind(text: str) -> str:
    lowered = str(text or "").lower()
    if any(token in lowered for token in ("monitor", "signal", "metric", "alert", "trace", "visibility", "observability")):
        return "monitoring"
    if any(token in lowered for token in ("retry", "timeout", "circuit", "fallback", "contain", "resilien", "backpressure", "queue", "lag")):
        return "resilience"
    if any(token in lowered for token in ("schema", "store", "state", "cache", "snapshot")):
        return "state"
    if any(token in lowered for token in ("dependency", "client", "api", "broker", "external")):
        return "dependency"
    return "architecture"


def build_failure_scenarios_from_candidates(facts_root: Path) -> list[dict[str, Any]]:
    payload = load_optional_json(facts_root / "failure-scenario-candidates.json")
    scenarios: list[dict[str, Any]] = []
    for candidate in payload.get("candidates") or []:
        if not isinstance(candidate, dict):
            continue
        candidate_id = str(candidate.get("id") or "").strip()
        if not candidate_id:
            continue
        starts_at = unique_strings([str(item) for item in (candidate.get("starts_at") or []) if item])
        involves = unique_strings([str(item) for item in (candidate.get("involves") or []) if item])
        chain = [
            {
                "from": str(step.get("from") or ""),
                "to": str(step.get("to") or ""),
                "effect": str(step.get("effect") or "").strip(),
            }
            for step in (candidate.get("chain") or [])
            if isinstance(step, dict) and str(step.get("from") or "").strip() and str(step.get("to") or "").strip() and str(step.get("effect") or "").strip()
        ]
        scenarios.append(
            {
                "id": candidate_id,
                "name": titleize_slug(candidate_id),
                "scope": str(candidate.get("scope") or "cascading"),
                "starts_at": starts_at,
                "involves": involves,
                "chain": chain,
                "degraded_mode": str(candidate.get("degraded_mode_hint") or "").strip()
                or "Shared system behavior becomes delayed, stale, partial, or unavailable across the involved units.",
                "mitigations": unique_strings(
                    [str(item) for item in (candidate.get("mitigation_hints") or []) if item]
                    + ([str(candidate.get("containment_hint"))] if str(candidate.get("containment_hint") or "").strip() else [])
                ),
                "grounded_in": unique_strings([source_line(str(ref)) for ref in (candidate.get("evidence_refs") or []) if ref]),
            }
        )
    return scenarios


def collect_monitoring_from_health(
    target: dict[str, Any],
    target_kind: str,
    monitoring_entries: list[dict[str, Any]],
) -> None:
    health = target.get("health")
    if not isinstance(health, dict):
        return
    target_id = str(target.get("id") or "").strip()
    if not target_id:
        return
    signals = unique_strings([str(item) for item in (health.get("signals") or []) if item])
    if not signals:
        return
    name = str(target.get("name") or titleize_slug(target_id))
    grounded: list[str] = []
    for ref in target.get("grounded_in") or []:
        grounded.append(source_line(str(ref)))
    for block_name in ("local", "integration"):
        block = health.get(block_name) if isinstance(health.get(block_name), dict) else {}
        for failure_mode in block.get("failure_modes") or []:
            if isinstance(failure_mode, dict):
                grounded.extend(source_line(str(ref)) for ref in (failure_mode.get("grounded_in") or []) if ref)
    monitoring_entries.append(
        {
            "id": f"{target_id}-health-monitoring",
            "name": f"{name} health monitoring",
            "kind": "signal",
            "summary": f"Tracks whether {name} still satisfies its healthy-operation criteria and exposes early degradation symptoms.",
            "covers": [target_id],
            "signals": signals,
            "grounded_in": unique_strings(grounded),
        }
    )


def collect_unit_gaps(
    target: dict[str, Any],
    gaps: list[dict[str, Any]],
) -> None:
    health = target.get("health")
    if not isinstance(health, dict):
        return
    target_id = str(target.get("id") or "").strip()
    if not target_id:
        return
    grounded: list[str] = [source_line(str(ref)) for ref in (target.get("grounded_in") or []) if ref]
    collected = [str(item) for item in (health.get("gaps") or []) if str(item or "").strip()]
    for block_name in ("local", "integration"):
        block = health.get(block_name) if isinstance(health.get(block_name), dict) else {}
        for failure_mode in block.get("failure_modes") or []:
            if not isinstance(failure_mode, dict):
                continue
            collected.extend(str(item) for item in (failure_mode.get("gaps") or []) if str(item or "").strip())
            grounded.extend(source_line(str(ref)) for ref in (failure_mode.get("grounded_in") or []) if ref)
    for scenario in ((health.get("propagation") or {}).get("scenarios") or []):
        if not isinstance(scenario, dict):
            continue
        collected.extend(str(item) for item in (scenario.get("gaps") or []) if str(item or "").strip())
        grounded.extend(source_line(str(ref)) for ref in (scenario.get("grounded_in") or []) if ref)

    for idx, text in enumerate(unique_strings(collected), start=1):
        gaps.append(
            {
                "id": f"{target_id}-{slugify(text)[:48] or idx}-gap",
                "kind": classify_gap_kind(text),
                "title": f"{titleize_slug(target_id)} gap",
                "summary": text,
                "affects": [target_id],
                "recommendation": "Add the missing control, monitoring, or resilience mechanism described by this gap.",
                "grounded_in": unique_strings(grounded),
            }
        )


def collect_flow_business_monitoring(flows: list[dict[str, Any]], monitoring_entries: list[dict[str, Any]]) -> None:
    for flow in flows:
        flow_id = str(flow.get("id") or "").strip()
        if not flow_id:
            continue
        for metric in flow.get("business_metrics") or []:
            if not isinstance(metric, dict) or not metric.get("name"):
                continue
            metric_name = str(metric.get("name") or "").strip()
            if not metric_name:
                continue
            monitoring_entries.append(
                {
                    "id": f"{flow_id}-{slugify(metric_name)}-monitoring",
                    "name": metric_name,
                    "kind": "metric",
                    "summary": str(metric.get("description") or f"Tracks business-visible outcomes for {flow.get('name') or flow_id}.").strip(),
                    "covers": [flow_id],
                    "signals": [metric_name],
                    "grounded_in": unique_strings([source_line(str(ref)) for ref in (metric.get("grounded_in") or []) if ref]),
                }
            )


def collect_failure_scenario_monitoring_and_gaps(
    failure_scenarios: list[dict[str, Any]],
    candidate_payload: dict[str, Any],
    monitoring_entries: list[dict[str, Any]],
    gaps: list[dict[str, Any]],
) -> None:
    candidates = {
        str(candidate.get("id") or ""): candidate
        for candidate in (candidate_payload.get("candidates") or [])
        if isinstance(candidate, dict) and candidate.get("id")
    }
    for scenario in failure_scenarios:
        scenario_id = str(scenario.get("id") or "").strip()
        if not scenario_id:
            continue
        candidate = candidates.get(scenario_id) or {}
        signal_hints = unique_strings([str(item) for item in (candidate.get("signal_hints") or []) if item])
        grounded = unique_strings([source_line(str(ref)) for ref in (scenario.get("grounded_in") or []) if ref])
        if signal_hints:
            monitoring_entries.append(
                {
                    "id": f"{scenario_id}-monitoring",
                    "name": f"{titleize_slug(scenario_id)} monitoring",
                    "kind": "alert",
                    "summary": f"Signals that reveal whether the shared failure scenario {titleize_slug(scenario_id)} is beginning or actively degrading the system.",
                    "covers": [scenario_id],
                    "signals": signal_hints,
                    "grounded_in": grounded,
                }
            )
        for idx, text in enumerate(unique_strings([str(item) for item in (candidate.get("gaps") or []) if item]), start=1):
            gaps.append(
                {
                    "id": f"{scenario_id}-{slugify(text)[:48] or idx}-gap",
                    "kind": classify_gap_kind(text),
                    "title": f"{titleize_slug(scenario_id)} gap",
                    "summary": text,
                    "affects": unique_strings([scenario_id] + [str(item) for item in (scenario.get("involves") or []) if item]),
                    "recommendation": "Add the missing monitoring, guardrail, or containment needed for this shared failure scenario.",
                    "grounded_in": grounded,
                }
            )


def migrate_observability_contract(output: dict[str, Any], facts_root: Path) -> None:
    failure_scenarios = build_failure_scenarios_from_candidates(facts_root)
    scenario_starts: dict[str, list[str]] = {}
    scenario_involves: dict[str, list[str]] = {}
    for scenario in failure_scenarios:
        sid = str(scenario.get("id") or "")
        for entity in scenario.get("starts_at") or []:
            scenario_starts.setdefault(str(entity), []).append(sid)
        for entity in scenario.get("involves") or []:
            scenario_involves.setdefault(str(entity), []).append(sid)

    monitoring_entries: list[dict[str, Any]] = []
    gaps: list[dict[str, Any]] = []
    failure_scenario_candidates_payload = load_optional_json(facts_root / "failure-scenario-candidates.json")

    for section_name in ("components", "flows", "external_dependencies"):
        for item in output.get(section_name) or []:
            if not isinstance(item, dict):
                continue
            item_id = str(item.get("id") or "").strip()
            if not item_id:
                continue
            health = item.get("health") if isinstance(item.get("health"), dict) else {}
            collect_monitoring_from_health(item, section_name.rstrip("s"), monitoring_entries)
            collect_unit_gaps(item, gaps)
            item["health"] = {
                "criteria": unique_strings([str(v) for v in (health.get("criteria") or []) if v]),
                "triggers_failure_scenarios": unique_strings(scenario_starts.get(item_id, [])),
                "participates_in_failure_scenarios": unique_strings(
                    [sid for sid in scenario_involves.get(item_id, []) if sid not in set(scenario_starts.get(item_id, []))]
                ),
            }

    collect_flow_business_monitoring([item for item in (output.get("flows") or []) if isinstance(item, dict)], monitoring_entries)
    collect_failure_scenario_monitoring_and_gaps(failure_scenarios, failure_scenario_candidates_payload, monitoring_entries, gaps)

    concepts = output.get("concepts") if isinstance(output.get("concepts"), dict) else {}
    concept_gap_entries = concepts.pop("gaps", []) if isinstance(concepts.get("gaps"), list) else []
    for gap in concept_gap_entries:
        if not isinstance(gap, dict):
            continue
        gap_id = str(gap.get("id") or "").strip()
        relevance = str(gap.get("relevance") or "").strip()
        recommendation = str(gap.get("recommendation") or "").strip()
        grounded = unique_strings([source_line(str(ref)) for ref in (gap.get("grounded_in") or []) if ref])
        evidence = gap.get("evidence") or {}
        grounded.extend(source_line(str(ref)) for ref in (evidence.get("files") or []) if ref)
        gaps.append(
            {
                "id": gap_id or f"concept-gap-{len(gaps) + 1}",
                "kind": "concept",
                "title": titleize_slug(gap_id or "concept-gap"),
                "summary": relevance or "Expected concept support is missing or weak in the current architecture.",
                "affects": unique_strings([str(item) for item in (gap.get("components") or []) if item] + ([gap_id] if gap_id else [])),
                "recommendation": recommendation or "Add the missing concept support or architectural treatment suggested by this gap.",
                "grounded_in": unique_strings(grounded),
            }
        )

    for anti_pattern in concepts.get("detected_anti_patterns") or []:
        if not isinstance(anti_pattern, dict):
            continue
        anti_id = str(anti_pattern.get("id") or "").strip()
        summary = str(anti_pattern.get("summary") or "").strip()
        why = str(anti_pattern.get("why_it_matters") or "").strip()
        grounded = unique_strings([source_line(str(ref)) for ref in (anti_pattern.get("grounded_in") or []) if ref])
        gaps.append(
            {
                "id": f"{anti_id}-anti-pattern-gap" if anti_id else f"anti-pattern-gap-{len(gaps) + 1}",
                "kind": "anti-pattern",
                "title": titleize_slug(anti_id or "anti-pattern"),
                "summary": summary or why or "A grounded anti-pattern materially weakens the current architecture.",
                "affects": unique_strings(
                    [str(item) for item in (anti_pattern.get("components") or []) if item]
                    + [str(item) for item in (anti_pattern.get("flows") or []) if item]
                    + [str(item) for item in (anti_pattern.get("state") or []) if item]
                    + ([anti_id] if anti_id else [])
                ),
                "recommendation": why or "Address the anti-pattern or explain the intentional trade-off that keeps it in place.",
                "grounded_in": grounded,
            }
        )

    output["failure_scenarios"] = failure_scenarios
    output["monitoring"] = list({entry["id"]: {**entry, "signals": unique_strings(entry.get("signals") or []), "covers": unique_strings(entry.get("covers") or []), "grounded_in": unique_strings(entry.get("grounded_in") or [])} for entry in monitoring_entries if isinstance(entry, dict) and entry.get("id")}.values())
    output["gaps"] = list({entry["id"]: {**entry, "affects": unique_strings(entry.get("affects") or []), "grounded_in": unique_strings(entry.get("grounded_in") or [])} for entry in gaps if isinstance(entry, dict) and entry.get("id")}.values())


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
    evidence = raw.get("evidence") or {}
    if not isinstance(evidence, dict):
        evidence = {}
    review = raw.get("review") or {}
    if not isinstance(review, dict):
        review = {}

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
        "evidence": evidence,
        "review": review,
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
        evidence = item.get("evidence") or {}
        if not isinstance(evidence, dict):
            evidence = {}
        supporting = evidence.get("supporting") or {}
        if not isinstance(supporting, dict):
            supporting = {}
        review = item.get("review") or {}
        if not isinstance(review, dict):
            review = {}
        concept_id = raw.get("concept_id")
        if not isinstance(concept_id, str) or not concept_id:
            continue
        patterns.append({
            "id": concept_id,
            "category": str(raw.get("category") or "unknown"),
            "confidence": str(item.get("confidence") or "low"),
            "decision_mode": str(raw.get("decision_mode") or "fact-inference"),
            "review_required": bool(review.get("required")),
            "detector_backing": str(supporting.get("detector_backing") or "weak"),
            "summary": str(raw.get("note") or f"{concept_id} is suggested by deterministic fact evidence in this repo."),
            "why_it_matters": str(raw.get("note") or "This concept materially shapes the architecture or integration boundaries."),
            "components": item.get("relationships", {}).get("component_ids") if isinstance(item.get("relationships"), dict) else [],
            "flows": [],
            "state": [],
            "grounded_in": [f"{path}:1" for path in (item.get("source_files") or [])[:3]],
            "evidence": {
                "fact_ids": supporting.get("fact_ids") or item.get("relationships", {}).get("depends_on_fact_ids") if isinstance(item.get("relationships"), dict) else [],
                "files": item.get("source_files") or [],
                "components": supporting.get("component_ids") or [],
                "method": raw.get("inference_method") or "inferred-from-facts",
                "detector_class": raw.get("detector_class") or "inference",
                "note": raw.get("note") or "",
                "questions_asked": (review.get("questions") or {}).get("entry_ids") if isinstance(review.get("questions"), dict) else [],
                "counter": [str(item) for item in evidence.get("counter") or [] if item],
                "gaps": [str(item) for item in evidence.get("gaps") or [] if item],
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

        frameworks.append(
            {
                "name": name,
                "language": language,
                "scope": str(raw.get("scope") or ""),
                "framework_kind": str(raw.get("framework_kind") or ""),
                "status": str(raw.get("status") or ""),
                "concepts": concepts,
            }
        )

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
                "summary": "",
                "criticality": str(raw.get("criticality") or "important"),
                "resilience": resilience,
                "health": {
                    "local": {
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
                    },
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
            if grounded and dependency.get("health", {}).get("local", {}).get("failure_modes"):
                for item in dependency["health"]["local"]["failure_modes"]:
                    item["grounded_in"] = unique_strings(list(item.get("grounded_in") or []) + sorted(grounded))
        component_text = ", ".join(dependency["components"][:3]) if dependency["components"] else "core runtime paths"
        purpose = str(dependency.get("purpose") or "").strip().rstrip(".")
        role = technology if technology and technology != "unknown" else concept.replace("-", " ")
        dependency["summary"] = (
            f"{name} provides a {role} capability that {component_text} relies on. "
            f"It matters here because {purpose.lower() if purpose else 'important application paths depend on it'}."
        )
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
                    "local": {"failure_modes": merge_failure_modes(bucket["health_failure_modes"])},
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
                "health": {"local": {"failure_modes": []}, "gaps": []},
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
        if edge_facts and len(edge_facts) > 3 and flow.get("health", {}).get("local", {}).get("failure_modes"):
            flow["health"]["local"]["failure_modes"][0]["signals"] = unique_strings(
                list(flow["health"]["local"]["failure_modes"][0].get("signals") or []) + ["call.path.depth"]
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
                "local": {
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
                },
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
                "local": {
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
                },
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
                "local": {
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
                },
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
        "stack_summary": runtime,
    }


def derive_technologies(
    facts: list[dict[str, Any]],
    state: list[dict[str, Any]],
    external_dependencies: list[dict[str, Any]],
) -> list[str]:
    values: list[str] = []
    for fact in facts:
        raw = fact.get("raw_evidence") or {}
        tech = str(raw.get("technology") or "").strip()
        if tech:
            values.append(tech)
    for entry in state:
        tech = str(entry.get("technology") or "").strip()
        if tech:
            values.append(tech)
    for dep in external_dependencies:
        tech = str(dep.get("technology") or "").strip()
        if tech:
            values.append(tech)
    normalized = unique_strings([value for value in values if value])
    return normalized[:16]


def selected_patterns(patterns: list[dict[str, Any]]) -> list[dict[str, Any]]:
    selected: list[dict[str, Any]] = []
    for pattern in patterns:
        verdict = pattern.get("verdict") or {}
        verdict_value = str(verdict.get("verdict") or "").strip().lower()
        if verdict_value in {"confirmed", "candidate"} or not verdict_value:
            selected.append(pattern)
    return selected


def concept_monitoring_eligible(pattern: dict[str, Any]) -> bool:
    verdict = pattern.get("verdict") or {}
    verdict_value = str(verdict.get("verdict") or "").strip().lower()
    if verdict_value == "confirmed":
        return True
    detector_backing = str(pattern.get("detector_backing") or "weak").strip().lower()
    confidence = str(pattern.get("confidence") or "low").strip().lower()
    decision_mode = str(pattern.get("decision_mode") or "fact-inference").strip().lower()
    review_required = bool(pattern.get("review_required"))
    if detector_backing == "weak":
        return False
    if decision_mode == "semantic-review" and review_required:
        return detector_backing == "strong" and confidence == "high"
    if detector_backing == "strong" and confidence in {"medium", "high"}:
        return True
    if detector_backing == "partial" and confidence == "high":
        return True
    return False


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
    observed_signals: list[str],
    missing_gaps: list[str],
) -> None:
    health = target.setdefault("health", {})
    existing_gaps = health.get("gaps") or []
    local = health.setdefault("local", {})
    existing_failure_modes = local.get("failure_modes") or []
    health["gaps"] = unique_strings(existing_gaps + [str(item) for item in monitoring.get("gaps") or [] if item] + missing_gaps)

    failure_mode_id = f"{target.get('id', 'entity')}-{slugify(concept_id)}-runtime"
    if not any(isinstance(item, dict) and item.get("id") == failure_mode_id for item in existing_failure_modes):
        signals = observed_signals
        gaps = [str(item) for item in monitoring.get("gaps") or [] if item]
        if missing_gaps:
            gaps = unique_strings(gaps + missing_gaps)
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
    local["failure_modes"] = merge_failure_modes(existing_failure_modes)


def attach_concept_monitoring(
    components: list[dict[str, Any]],
    external_dependencies: list[dict[str, Any]],
    flows: list[dict[str, Any]],
    patterns: list[dict[str, Any]],
    monitoring_index: dict[str, dict[str, Any]],
    repo_root: Path | None,
) -> None:
    component_map = {component.get("id"): component for component in components if component.get("id")}

    for pattern in selected_patterns(patterns):
        concept_id = str(pattern.get("id") or "")
        monitoring = monitoring_index.get(concept_id)
        if not monitoring:
            continue
        if not concept_monitoring_eligible(pattern):
            continue
        applies_to = {str(item) for item in monitoring.get("applies_to") or [] if item}
        component_ids = [str(item) for item in pattern.get("components") or [] if item]
        grounded_in = pattern_grounding(pattern)
        observed_signals, observed_metrics, missing_gaps = evaluate_monitoring_expectations(
            repo_root,
            pattern,
            monitoring,
            component_map,
        )

        if "component" in applies_to:
            for component_id in component_ids:
                component = component_map.get(component_id)
                if component:
                    append_concept_health(component, "component", concept_id, monitoring, grounded_in, observed_signals, missing_gaps)

        if "dependency" in applies_to and component_ids:
            component_set = set(component_ids)
            for dependency in external_dependencies:
                dependency_components = {str(item) for item in dependency.get("components") or [] if item}
                if dependency_components & component_set:
                    append_concept_health(dependency, "external-dependency", concept_id, monitoring, grounded_in, observed_signals, missing_gaps)

        if "flow" in applies_to:
            for flow in flows:
                flow_components = {
                    str(step.get("component"))
                    for step in flow.get("steps") or []
                    if isinstance(step, dict) and step.get("component")
                }
                if flow_components & set(component_ids):
                    append_concept_health(flow, "flow", concept_id, monitoring, grounded_in, observed_signals, missing_gaps)
                    flow.setdefault("business_metrics", [])
                    for metric in observed_metrics:
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
    repo_root = Path(str(index.get("root") or "")).resolve() if isinstance(index, dict) and index.get("root") else None

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
            repo_root,
        )
    if not purpose:
        purpose = f"{project} system synthesized from extracted facts." if project else "System synthesized from extracted facts."

    stack = build_stack(facts)
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
        "stack_summary": stack.get("stack_summary", ""),
        "languages": stack.get("languages", []),
        "frameworks": [
            {
                "name": str(item.get("name") or ""),
                "language": str(item.get("language") or ""),
                "framework_kind": str(item.get("framework_kind") or ""),
                "scope": str(item.get("scope") or ""),
                "status": "accepted",
            }
            for item in (stack.get("frameworks") or [])
            if isinstance(item, dict) and item.get("name")
        ],
        "technologies": derive_technologies(facts, state, external_dependencies),
    }

    concepts = {
        "detected_patterns": [],
        "detected_anti_patterns": [],
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
        "failure_scenarios": [],
        "monitoring": [],
        "gaps": [],
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
    if not seed_mode:
        migrate_observability_contract(output, facts_root)
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
