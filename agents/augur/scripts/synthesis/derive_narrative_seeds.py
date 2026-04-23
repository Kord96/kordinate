#!/usr/bin/env python3
"""Derive deterministic narrative-planning seeds from prepared fact artifacts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Derive Augur narrative seeds from deterministic facts")
    parser.add_argument("facts_dir", help="facts/ directory for the prepared run")
    parser.add_argument("--output", required=True, help="Output JSON path")
    return parser.parse_args()


def candidate_roots(component_payload: dict[str, Any]) -> list[dict[str, Any]]:
    ranked = []
    for seed in component_payload.get("candidate_components") or []:
        if not isinstance(seed, dict):
            continue
        root_likelihood = int(seed.get("root_likelihood") or 0)
        if root_likelihood < 4:
            continue
        ranked.append(
            {
                "id": str(seed.get("id") or ""),
                "group": str(seed.get("group") or seed.get("id") or ""),
                "root_likelihood": root_likelihood,
                "rationale": str(seed.get("rationale") or ""),
                "signals": list(seed.get("signals") or []),
                "representative_files": list(seed.get("representative_files") or [])[:3],
            }
        )
    ranked.sort(
        key=lambda item: (
            -int(item.get("root_likelihood") or 0),
            -len(item.get("signals") or []),
            item.get("group") or item.get("id") or "",
        )
    )
    return ranked[:4]


def concern_summary(story_payload: dict[str, Any]) -> tuple[list[str], bool, bool, bool]:
    preferred: list[str] = []
    require_flow_story = False
    require_state_or_boundary_story = False
    prefer_child_stories = False

    for item in story_payload.get("candidate_concern_classes") or []:
        if not isinstance(item, dict):
            continue
        concern_class = str(item.get("class") or "").strip()
        if not concern_class:
            continue
        preferred.append(concern_class)
        if concern_class in {"request-or-control-flow", "background-or-event-path"}:
            require_flow_story = True
        if concern_class in {"state-boundary", "dependency-or-operations-boundary"}:
            require_state_or_boundary_story = True
        if concern_class in {
            "request-or-control-flow",
            "background-or-event-path",
            "state-boundary",
            "dependency-or-operations-boundary",
        }:
            prefer_child_stories = True

    deduped: list[str] = []
    seen: set[str] = set()
    for concern_class in preferred:
        if concern_class in seen:
            continue
        seen.add(concern_class)
        deduped.append(concern_class)

    return deduped, require_flow_story, require_state_or_boundary_story, prefer_child_stories


def normalize_file_refs(items: list[Any]) -> list[str]:
    refs: list[str] = []
    seen: set[str] = set()
    for item in items:
        candidates: list[str] = []
        if isinstance(item, str):
            candidates.append(item)
        elif isinstance(item, dict):
            source_files = [str(ref) for ref in (item.get("source_files") or []) if ref]
            if source_files:
                candidates.extend(source_files)
            raw = item.get("raw_evidence") or {}
            file_ref = str(raw.get("file") or raw.get("slice_file") or "").strip()
            if file_ref:
                candidates.append(file_ref)
        for candidate in candidates:
            candidate = candidate.strip()
            if candidate and candidate not in seen:
                seen.add(candidate)
                refs.append(candidate)
    return refs


def hotspot_summary(payload: dict[str, Any]) -> list[dict[str, Any]]:
    ranked: list[dict[str, Any]] = []
    for fact in payload.get("facts") or []:
        if not isinstance(fact, dict):
            continue
        raw = fact.get("raw_evidence") or {}
        component = str(raw.get("component") or "").strip()
        slice_file = str(raw.get("slice_file") or "").strip()
        if not component or not slice_file:
            continue
        ranked.append(
            {
                "component": component,
                "slice_file": slice_file,
                "slice_count": int(raw.get("slice_count") or 0),
                "average_steps": raw.get("average_steps"),
                "slice_names": list(raw.get("slice_names") or [])[:3],
                "source_files": list(fact.get("source_files") or [])[:3],
            }
        )
    ranked.sort(
        key=lambda item: (
            -int(item.get("slice_count") or 0),
            -(float(item.get("average_steps") or 0.0)),
            item.get("component") or "",
        )
    )
    return ranked[:4]


def boundary_summary(payload: dict[str, Any]) -> list[dict[str, Any]]:
    ranked: list[dict[str, Any]] = []
    for fact in payload.get("facts") or []:
        if not isinstance(fact, dict):
            continue
        raw = fact.get("raw_evidence") or {}
        target_name = str(raw.get("target_name") or "").strip()
        components = [str(item) for item in (raw.get("components") or []) if item]
        if not target_name or not components:
            continue
        ranked.append(
            {
                "target_name": target_name,
                "touch_kind": str(raw.get("touch_kind") or ""),
                "components": components[:4],
                "touch_count": int(raw.get("touch_count") or 0),
                "source_files": list(fact.get("source_files") or [])[:3],
            }
        )
    ranked.sort(
        key=lambda item: (
            -int(item.get("touch_count") or 0),
            -len(item.get("components") or []),
            item.get("target_name") or "",
        )
    )
    return ranked[:4]


def main() -> int:
    args = parse_args()
    facts_dir = Path(args.facts_dir).resolve()
    output_path = Path(args.output).resolve()
    run_dir = facts_dir.parent
    derived_dir = run_dir / "derived"

    component_payload = load_json(derived_dir / "component-seeds.json") if (derived_dir / "component-seeds.json").exists() else {}
    story_payload = load_json(derived_dir / "story-seeds.json") if (derived_dir / "story-seeds.json").exists() else {}
    control_hotspots_payload = load_json(facts_dir / "control-hotspots.json") if (facts_dir / "control-hotspots.json").exists() else {}
    state_access_summary_payload = load_json(facts_dir / "state-access-summary.json") if (facts_dir / "state-access-summary.json").exists() else {}
    concepts_payload = load_json(facts_dir / "concepts.json") if (facts_dir / "concepts.json").exists() else {}
    health_candidates_payload = load_json(facts_dir / "health-candidates.json") if (facts_dir / "health-candidates.json").exists() else {}
    index_payload = load_json(run_dir / "index.json") if (run_dir / "index.json").exists() else {}

    preferred_concern_classes, require_flow_story, require_state_or_boundary_story, prefer_child_stories = concern_summary(story_payload)
    starter_files = normalize_file_refs(list(story_payload.get("starter_files") or []))[:8]
    hot_files = normalize_file_refs(list(story_payload.get("hot_files") or []))[:8]
    preferred_flow_hotspots = hotspot_summary(control_hotspots_payload)
    preferred_state_or_boundary_targets = boundary_summary(state_access_summary_payload)

    present_domains = {
        str(item.get("name") or "")
        for item in ((index_payload.get("index") or {}).get("domains") or [])
        if isinstance(item, dict)
    }
    accepted_concepts = {
        str((fact.get("raw_evidence") or {}).get("concept_id") or fact.get("id") or "")
        for fact in (concepts_payload.get("facts") or [])
        if isinstance(fact, dict)
        and str((fact.get("raw_evidence") or {}).get("decision_mode") or "") in {"accepted", "semantic-review"}
    }

    recommended_narratives: list[dict[str, Any]] = [
        {
            "id": "system-overview",
            "required": True,
            "score": 100,
            "reason": "Every repo needs one canonical narrative that explains what the system does and how its main architecture achieves that outcome.",
            "evidence": {
                "preferred_root_components": [item.get("id") for item in candidate_roots(component_payload)],
                "preferred_flow_hotspots": [item.get("component") for item in preferred_flow_hotspots],
                "preferred_state_or_boundary_targets": [item.get("target_name") for item in preferred_state_or_boundary_targets],
            },
        }
    ]

    def add_recommended_narrative(
        narrative_id: str,
        *,
        score: int,
        reason: str,
        evidence: dict[str, Any],
    ) -> None:
        recommended_narratives.append(
            {
                "id": narrative_id,
                "required": False,
                "score": int(score),
                "reason": reason,
                "evidence": evidence,
            }
        )

    runtime_domains = {"routes", "handlers", "jobs", "events"} & present_domains
    if preferred_flow_hotspots or len(runtime_domains) >= 3:
        add_recommended_narrative(
            "runtime-paths",
            score=(
                26
                + min(18, 6 * len(preferred_flow_hotspots))
                + min(20, 5 * len(runtime_domains))
            ),
            reason="Deterministic control, request, scheduler, or event evidence suggests the repo benefits from a narrative focused on how execution actually moves.",
            evidence={
                "flow_hotspots": [item.get("component") for item in preferred_flow_hotspots],
                "domains": sorted(runtime_domains),
            },
        )

    if preferred_state_or_boundary_targets or "state-access-summary" in present_domains:
        add_recommended_narrative(
            "state-and-data",
            score=(
                32
                + min(18, 6 * len(preferred_state_or_boundary_targets))
                + (12 if "state-access-summary" in present_domains else 0)
            ),
            reason="Deterministic state-access evidence suggests persistence or data boundaries deserve their own teaching path.",
            evidence={
                "targets": [item.get("target_name") for item in preferred_state_or_boundary_targets],
                "domains": sorted({"state-access-summary"} & present_domains),
            },
        )

    if "external-clients" in present_domains and (
        preferred_state_or_boundary_targets or "dependency-or-operations-boundary" in preferred_concern_classes
    ):
        add_recommended_narrative(
            "integrations",
            score=(
                28
                + (12 if "external-clients" in present_domains else 0)
                + (10 if "dependency-or-operations-boundary" in preferred_concern_classes else 0)
                + min(12, 4 * len(preferred_state_or_boundary_targets))
            ),
            reason="External-client or boundary evidence suggests the repo has important dependency seams or protocol handoffs worth isolating.",
            evidence={
                "domains": sorted({"external-clients"} & present_domains),
                "concern_classes": [item for item in preferred_concern_classes if item == "dependency-or-operations-boundary"],
            },
        )

    local_candidate_count = len(health_candidates_payload.get("local_candidates") or [])
    integration_candidate_count = len(health_candidates_payload.get("integration_candidates") or [])
    propagation_candidate_count = len(health_candidates_payload.get("propagation_candidates") or [])
    if any(
        (health_candidates_payload.get(key) or [])
        for key in ("local_candidates", "integration_candidates", "propagation_candidates")
    ):
        add_recommended_narrative(
            "operations-and-failure",
            score=(
                34
                + min(8, 2 * local_candidate_count)
                + min(22, integration_candidate_count)
                + min(18, 6 * propagation_candidate_count)
            ),
            reason="Layered health candidates suggest a narrative focused on degraded modes, seams, and observability.",
            evidence={
                "local_candidates": local_candidate_count,
                "integration_candidates": integration_candidate_count,
                "propagation_candidates": propagation_candidate_count,
            },
        )

    if accepted_concepts & {"plugin-system", "command-dispatch", "service-manager"}:
        add_recommended_narrative(
            "extensibility",
            score=40 + min(18, 6 * len(accepted_concepts & {"plugin-system", "command-dispatch", "service-manager"})),
            reason="Dispatch or extensibility evidence suggests the repo exposes meaningful composition or extension seams.",
            evidence={
                "concepts": sorted(accepted_concepts & {"plugin-system", "command-dispatch", "service-manager"}),
            },
        )

    if accepted_concepts & {"oauth-oidc", "token-auth", "session-auth", "rbac"}:
        add_recommended_narrative(
            "security-and-access",
            score=42 + min(18, 6 * len(accepted_concepts & {"oauth-oidc", "token-auth", "session-auth", "rbac"})),
            reason="Security-related concept evidence suggests identity, token, or access-control flows are important enough to deserve a separate teaching path.",
            evidence={
                "concepts": sorted(accepted_concepts & {"oauth-oidc", "token-auth", "session-auth", "rbac"}),
            },
        )

    recommended_narratives.sort(
        key=lambda item: (
            -int(item.get("score") or 0),
            0 if bool(item.get("required")) else 1,
            str(item.get("id") or ""),
        )
    )
    for index, item in enumerate(recommended_narratives, start=1):
        item["priority_rank"] = index

    optional_recommended = [item for item in recommended_narratives if not bool(item.get("required"))]
    preferred_optional_count = 0
    if optional_recommended:
        strongest_score = int(optional_recommended[0].get("score") or 0)
        preferred_optional_count = 1
        if len(optional_recommended) > 1:
            runner_up_score = int(optional_recommended[1].get("score") or 0)
            if strongest_score >= 55 and runner_up_score >= 55 and strongest_score - runner_up_score <= 8:
                preferred_optional_count = 2

    payload = {
        "version": 1,
        "goal": "Advisory narrative-planning seeds derived from deterministic facts.",
        "recommended_narratives": recommended_narratives,
        "optional_narrative_budget": {
            "target": preferred_optional_count,
            "max": max(preferred_optional_count, 1 if optional_recommended else 0),
        },
        "system_overview": {
            "recommended_story_budget": {
                "min": 2,
                "target": 3,
                "max": 4,
            },
            "preferred_root_components": candidate_roots(component_payload),
            "preferred_concern_classes": preferred_concern_classes,
            "preferred_flow_hotspots": preferred_flow_hotspots,
            "preferred_state_or_boundary_targets": preferred_state_or_boundary_targets,
            "require_flow_story": require_flow_story,
            "require_state_or_boundary_story": require_state_or_boundary_story,
            "prefer_child_stories": prefer_child_stories,
            "selection_rules": [
                "Use the smallest set of stories that teaches system shape plus the operating model.",
                "Prefer a child story over a root story when the child better explains a defining flow, state boundary, or external dependency boundary.",
                "Avoid cataloging every top-level component in system-overview; choose the roots and children that best establish the first mental model.",
                "Treat control hotspots and state/boundary summaries as ranking hints for selection, not as a script to restate literally.",
            ],
            "starter_files": starter_files,
            "hot_files": hot_files,
            "questions": [
                "Which provisional roots are central enough to anchor the first mental model of the system?",
                "Which selected story best explains how the system actually moves, not just how it is partitioned?",
                "Which child story should replace a root story in system-overview because it teaches the architecture more clearly?",
            ],
        },
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
