#!/usr/bin/env python3
"""Derive deterministic health-planning candidates from prepared fact artifacts."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Any


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Derive Augur health candidates from deterministic facts")
    parser.add_argument("facts_dir", help="facts/ directory for the prepared run")
    parser.add_argument("--output", required=True, help="Output JSON path")
    return parser.parse_args()


def domain_facts(facts_dir: Path, name: str) -> list[dict[str, Any]]:
    path = facts_dir / f"{name}.json"
    if not path.exists():
        return []
    try:
        payload = load_json(path)
    except Exception:
        return []
    return [fact for fact in (payload.get("facts") or []) if isinstance(fact, dict)]


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


def top_component_ids(facts: list[dict[str, Any]]) -> list[str]:
    ordered: list[str] = []
    seen: set[str] = set()
    for fact in facts:
        relationships = fact.get("relationships") or {}
        for component_id in relationships.get("component_ids") or []:
            component_id = str(component_id or "").strip()
            if component_id and component_id not in seen:
                seen.add(component_id)
                ordered.append(component_id)
    return ordered


def local_candidates(
    frameworks: list[dict[str, Any]],
    jobs: list[dict[str, Any]],
    config: list[dict[str, Any]],
    routes: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    candidates: dict[str, dict[str, Any]] = {}

    def ensure(component_id: str) -> dict[str, Any]:
        return candidates.setdefault(
            component_id,
            {
                "id": stable_id(component_id, "local"),
                "component": component_id,
                "signals": [],
                "gaps": [],
                "triggers": [],
                "recovery_hints": [],
                "evidence_refs": [],
                "severity": "medium",
                "rationale": "",
            },
        )

    for fact in frameworks:
        raw = fact.get("raw_evidence") or {}
        failure_modes = [str(item) for item in (raw.get("common_failure_modes") or []) if item]
        if not failure_modes:
            continue
        signals = [str(item) for item in (raw.get("signals") or [])[:3] if item]
        for component_id in top_component_ids([fact]):
            bucket = ensure(component_id)
            bucket["triggers"].extend(failure_modes[:3])
            bucket["signals"].extend(signals)
            bucket["evidence_refs"].extend(str(item) for item in fact.get("source_files") or [] if item)
            bucket["rationale"] = f"Framework context and common failure modes suggest {component_id} has meaningful local runtime risks."

    for fact in jobs:
        raw = fact.get("raw_evidence") or {}
        job_type = str(raw.get("job_type") or "").strip()
        if not job_type:
            continue
        for component_id in top_component_ids([fact]):
            bucket = ensure(component_id)
            bucket["triggers"].append(f"{job_type}-loop-stalls")
            bucket["signals"].append(f"{job_type}_lag")
            bucket["gaps"].append(f"No explicit {job_type} health control is evident from deterministic facts.")
            bucket["evidence_refs"].extend(str(item) for item in fact.get("source_files") or [] if item)
            if job_type in {"scheduler", "worker"}:
                bucket["severity"] = "high"
                bucket["recovery_hints"].append(f"Restart or drain the {job_type} path and verify backlog clears.")
            if not bucket["rationale"]:
                bucket["rationale"] = f"Detected {job_type} facts suggest {component_id} has internal runtime loops worth modeling locally."

    config_counts: dict[str, int] = defaultdict(int)
    config_refs: dict[str, list[str]] = defaultdict(list)
    for fact in config:
        for component_id in top_component_ids([fact]):
            config_counts[component_id] += 1
            config_refs[component_id].extend(str(item) for item in fact.get("source_files") or [] if item)
    for component_id, count in config_counts.items():
        if count < 4:
            continue
        bucket = ensure(component_id)
        bucket["triggers"].append("config-drift-or-misconfiguration")
        bucket["signals"].append("config_reload_failed")
        bucket["gaps"].append("High config surface suggests failure modes should mention misconfiguration or drift explicitly.")
        bucket["evidence_refs"].extend(config_refs[component_id][:3])
        if not bucket["rationale"]:
            bucket["rationale"] = f"{component_id} has a broad configuration surface, so local health should model misconfiguration risk."

    route_counts: dict[str, int] = defaultdict(int)
    route_refs: dict[str, list[str]] = defaultdict(list)
    for fact in routes:
        for component_id in top_component_ids([fact]):
            route_counts[component_id] += 1
            route_refs[component_id].extend(str(item) for item in fact.get("source_files") or [] if item)
    for component_id, count in route_counts.items():
        if count < 6:
            continue
        bucket = ensure(component_id)
        bucket["signals"].append("request_error_rate")
        bucket["signals"].append("request_latency")
        bucket["gaps"].append("Large request surface suggests route-local health should mention request-path visibility.")
        bucket["evidence_refs"].extend(route_refs[component_id][:3])
        if not bucket["rationale"]:
            bucket["rationale"] = f"{component_id} exposes a broad request surface, so local health should mention request-path degradation."

    ranked = []
    for item in candidates.values():
        item["signals"] = unique_strings(item["signals"])
        item["gaps"] = unique_strings(item["gaps"])
        item["triggers"] = unique_strings(item["triggers"])
        item["recovery_hints"] = unique_strings(item["recovery_hints"])
        item["evidence_refs"] = unique_strings(item["evidence_refs"])[:4]
        ranked.append(item)
    ranked.sort(key=lambda item: (-len(item["evidence_refs"]), -len(item["signals"]), item["component"]))
    return ranked


def integration_candidates(
    state_access_summary: list[dict[str, Any]],
    external_clients: list[dict[str, Any]],
    routes: list[dict[str, Any]],
    dispatch_bindings: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    candidates: dict[tuple[str, str], dict[str, Any]] = {}

    def ensure(source: str, target: str, *, target_kind: str, rationale: str) -> dict[str, Any]:
        return candidates.setdefault(
            (source, target),
            {
                "id": stable_id(source, target, "integration"),
                "source": source,
                "target": target,
                "target_kind": target_kind,
                "signals": [],
                "gaps": [],
                "trigger_hints": [],
                "impact_hints": [],
                "evidence_refs": [],
                "severity": "medium",
                "rationale": rationale,
            },
        )

    for fact in state_access_summary:
        raw = fact.get("raw_evidence") or {}
        target = str(raw.get("target_name") or "").strip()
        if not target:
            continue
        touch_kind = str(raw.get("touch_kind") or "access").strip()
        for source in [str(item) for item in (raw.get("components") or []) if item]:
            bucket = ensure(
                source,
                stable_id(target),
                target_kind="state",
                rationale="Shared state access facts suggest a dependency seam that deserves integration health coverage.",
            )
            bucket["trigger_hints"].append(f"{touch_kind}-path-degrades")
            bucket["impact_hints"].append(f"{source} cannot rely on {target} behaving normally")
            bucket["signals"].append(f"{touch_kind}_latency")
            bucket["signals"].append(f"{touch_kind}_errors")
            bucket["evidence_refs"].extend(str(item) for item in fact.get("source_files") or [] if item)
            if int(raw.get("touch_count") or 0) >= 6:
                bucket["severity"] = "high"

    for fact in external_clients:
        raw = fact.get("raw_evidence") or {}
        technology = str(raw.get("target") or raw.get("technology") or "").strip()
        if not technology:
            continue
        for source in top_component_ids([fact]):
            target = stable_id(technology)
            bucket = ensure(
                source,
                target,
                target_kind="external_dependency",
                rationale="Outbound client facts suggest a runtime dependency seam that should be modeled explicitly.",
            )
            bucket["trigger_hints"].append("dependency-timeout-or-unavailable")
            bucket["impact_hints"].append(f"{source} cannot complete its dependency-backed path when {technology} degrades")
            timeout = str(raw.get("timeout") or "").strip()
            retry = str(raw.get("retry") or "").strip()
            circuit_breaker = str(raw.get("circuit_breaker") or "").strip()
            if timeout:
                bucket["signals"].append(timeout)
            if retry:
                bucket["signals"].append("retry_activity")
            if circuit_breaker:
                bucket["signals"].append("circuit_breaker_open")
            if not (retry or circuit_breaker):
                bucket["gaps"].append(f"No clear retry or circuit-breaker evidence for the {technology} seam.")
            bucket["evidence_refs"].extend(str(item) for item in fact.get("source_files") or [] if item)

    route_counts: dict[str, int] = defaultdict(int)
    route_refs: dict[str, list[str]] = defaultdict(list)
    for fact in routes:
        for component_id in top_component_ids([fact]):
            route_counts[component_id] += 1
            route_refs[component_id].extend(str(item) for item in fact.get("source_files") or [] if item)
    for component_id, count in route_counts.items():
        if count < 6:
            continue
        bucket = ensure(
            component_id,
            "client",
            target_kind="actor",
            rationale="A broad request surface implies an important caller-to-runtime seam that should be observable.",
        )
        bucket["trigger_hints"].append("request-contract-or-auth-path-fails")
        bucket["impact_hints"].append("Callers receive errors, stale responses, or partial data")
        bucket["signals"].append("request_error_rate")
        bucket["signals"].append("auth_failures")
        bucket["evidence_refs"].extend(route_refs[component_id][:3])

    for fact in dispatch_bindings:
        raw = fact.get("raw_evidence") or {}
        channel = str(raw.get("channel") or raw.get("target") or "").strip()
        if not channel:
            continue
        for source in top_component_ids([fact]):
            bucket = ensure(
                source,
                stable_id(channel),
                target_kind="dispatch_channel",
                rationale="Dispatch bindings expose runtime seams where queue or channel behavior can fail separately from local code.",
            )
            bucket["trigger_hints"].append("dispatch-channel-degrades")
            bucket["impact_hints"].append(f"{source} cannot push or receive work cleanly on {channel}")
            bucket["signals"].append("dispatch_failures")
            bucket["evidence_refs"].extend(str(item) for item in fact.get("source_files") or [] if item)

    ranked = []
    for item in candidates.values():
        item["signals"] = unique_strings(item["signals"])
        item["gaps"] = unique_strings(item["gaps"])
        item["trigger_hints"] = unique_strings(item["trigger_hints"])
        item["impact_hints"] = unique_strings(item["impact_hints"])
        item["evidence_refs"] = unique_strings(item["evidence_refs"])[:4]
        ranked.append(item)
    ranked.sort(key=lambda item: (-len(item["evidence_refs"]), item["source"], item["target"]))
    return ranked


def propagation_candidates(
    state_access_summary: list[dict[str, Any]],
    external_clients: list[dict[str, Any]],
    control_hotspots: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []

    state_buckets: dict[str, dict[str, Any]] = {}
    for fact in state_access_summary:
        raw = fact.get("raw_evidence") or {}
        target_name = str(raw.get("target_name") or "").strip()
        components = [str(item) for item in (raw.get("components") or []) if item]
        if not target_name or len(set(components)) < 2:
            continue
        bucket = state_buckets.setdefault(
            target_name,
            {"components": set(), "touch_count": 0, "refs": []},
        )
        bucket["components"].update(components)
        bucket["touch_count"] += int(raw.get("touch_count") or 0)
        bucket["refs"].extend(str(item) for item in fact.get("source_files") or [] if item)
    for target_name, bucket in state_buckets.items():
        components = sorted(bucket["components"])
        candidates.append(
            {
                "id": stable_id(target_name, "cascade"),
                "source": stable_id(target_name),
                "source_kind": "state",
                "affects": components,
                "degraded_mode_hint": f"Consumers may keep serving stale, incomplete, or delayed results when {target_name} degrades.",
                "containment_hint": "State-backed degradation should say whether callers can serve stale data, retry, or halt cleanly.",
                "rationale": "Shared state access facts indicate a real cascade surface across multiple components.",
                "evidence_refs": unique_strings(bucket["refs"])[:4],
                "touch_count": bucket["touch_count"],
            }
        )

    external_buckets: dict[str, dict[str, Any]] = {}
    for fact in external_clients:
        raw = fact.get("raw_evidence") or {}
        target = str(raw.get("target") or raw.get("technology") or "").strip()
        components = top_component_ids([fact])
        if not target or not components:
            continue
        bucket = external_buckets.setdefault(target, {"components": set(), "refs": []})
        bucket["components"].update(components)
        bucket["refs"].extend(str(item) for item in fact.get("source_files") or [] if item)
    for target, bucket in external_buckets.items():
        components = sorted(bucket["components"])
        if len(components) < 2:
            continue
        candidates.append(
            {
                "id": stable_id(target, "dependency-cascade"),
                "source": stable_id(target),
                "source_kind": "external_dependency",
                "affects": components,
                "degraded_mode_hint": f"Multiple components degrade together when {target} is unavailable.",
                "containment_hint": "Say whether retries, cached data, or staged work contain the outage or let it spread.",
                "rationale": "A shared external dependency suggests a multi-component cascade path.",
                "evidence_refs": unique_strings(bucket["refs"])[:4],
            }
        )

    hotspot_refs: dict[str, list[str]] = defaultdict(list)
    hotspot_counts: dict[str, int] = defaultdict(int)
    for fact in control_hotspots:
        raw = fact.get("raw_evidence") or {}
        component = str(raw.get("component") or "").strip()
        if not component:
            continue
        hotspot_counts[component] += int(raw.get("slice_count") or 0)
        hotspot_refs[component].extend(str(item) for item in fact.get("source_files") or [] if item)
    for component, slice_count in hotspot_counts.items():
        if slice_count < 4:
            continue
        candidates.append(
            {
                "id": stable_id(component, "control-cascade"),
                "source": component,
                "source_kind": "component",
                "affects": [component],
                "degraded_mode_hint": f"Critical execution chokepoints inside {component} can block or stall its downstream capabilities.",
                "containment_hint": "Explain whether failures are locally contained, retried, or spread to callers and dependents.",
                "rationale": "Control hotspots highlight execution chokepoints that deserve explicit degraded-mode thinking.",
                "evidence_refs": unique_strings(hotspot_refs[component])[:3],
            }
        )

    candidates.sort(key=lambda item: (-len(item.get("affects") or []), -len(item.get("evidence_refs") or []), item["source"]))
    return candidates


def main() -> int:
    args = parse_args()
    facts_dir = Path(args.facts_dir).resolve()
    output_path = Path(args.output).resolve()

    frameworks = domain_facts(facts_dir, "frameworks")
    jobs = domain_facts(facts_dir, "jobs")
    config = domain_facts(facts_dir, "config")
    routes = domain_facts(facts_dir, "routes")
    dispatch_bindings = domain_facts(facts_dir, "dispatch-bindings")
    external_clients = domain_facts(facts_dir, "external-clients")
    state_access_summary = domain_facts(facts_dir, "state-access-summary")
    control_hotspots = domain_facts(facts_dir, "control-hotspots")

    payload = {
        "version": 1,
        "goal": "Advisory layered health candidates derived from deterministic facts.",
        "local_candidates": local_candidates(frameworks, jobs, config, routes),
        "integration_candidates": integration_candidates(state_access_summary, external_clients, routes, dispatch_bindings),
        "propagation_candidates": propagation_candidates(state_access_summary, external_clients, control_hotspots),
        "selection_rules": [
            "Use candidates as coverage and grounding pressure, not as a script to restate literally.",
            "Prefer local health for failures internal to one component or dependency.",
            "Prefer integration health for failures at a boundary, seam, or dependency edge.",
            "Prefer propagation scenarios for downstream degraded modes, blast radius, or containment.",
        ],
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
