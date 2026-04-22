"""Classify issues and maintain append-only `log.json` history.

Checks owned here:
- normalize issue kinds and families for reporting
- derive stable issue ids for diffing/history
- append one structured validation snapshot per validator invocation
- summarize open consistency conflicts and repeated failures over time

This module does not inspect repo artifacts directly; it only organizes the
issues emitted by the real validators.
"""

import hashlib
import json
import re
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path


def classify_issue_kind(issue: dict) -> str:
    explicit_kind = str(issue.get("kind") or "").strip().lower()
    if explicit_kind:
        return explicit_kind
    section = str(issue.get("section") or "").lower()
    message = str(issue.get("message") or "").lower()
    if "non-existent path" in message or "non-existent file" in message:
        return "path-provenance"
    if "weak lexical overlap" in message or "weak code-shaped overlap" in message:
        return "grounding"
    if "under-decomposed" in message or "child" in message and "story" in section:
        return "story-decomposition"
    if "narrative" in section and "root stories" in message:
        return "narrative-selection"
    if section == "narrative" and "overview" in message:
        return "narrative-overview"
    if section == "narrative" and (
        "teaching goals" in message
        or "served by the selected stories" in message
        or "missing `teaches`" in message
    ):
        return "narrative-coherence"
    if "cycle" in message:
        return "graph-cycle"
    if section == "state" and ("too narrow" in message or "persistence" in message):
        return "state-truthfulness"
    if section == "concepts":
        return "concepts"
    if section == "components":
        return "component-model"
    if section == "flows":
        return "flow-model"
    if section == "story":
        return "story-quality"
    return section or "general"


def stable_issue_id(issue: dict) -> str:
    payload = "|".join(
        [
            str(issue.get("level") or ""),
            str(issue.get("section") or ""),
            classify_issue_kind(issue),
            str(issue.get("message") or ""),
        ]
    )
    return hashlib.sha1(payload.encode("utf-8")).hexdigest()[:12]


def grounding_group_label(issue: dict) -> str | None:
    if classify_issue_kind(issue) != "grounding":
        return None
    message = str(issue.get("message") or "")
    match = re.search(r"'([^']+)' grounding(?: at .+)? has weak code-shaped overlap", message)
    if match:
        return match.group(1)
    return None


def issue_family(issue: dict) -> str:
    kind = classify_issue_kind(issue)
    if kind in {"path-provenance", "concepts"}:
        return "provenance"
    if kind in {"grounding"}:
        return "grounding"
    if kind in {
        "health-criteria-missing",
        "health-scenario-link-missing",
        "health-scenario-link-invalid",
        "health-ownership-unclear",
        "failure-scenario-missing",
        "health-model",
        "monitoring-model",
        "gaps-model",
    }:
        return "health-model"
    if kind in {
        "story-decomposition",
        "narrative-selection",
        "narrative-overview",
        "narrative-coherence",
        "narrative-count",
        "story-quality",
    }:
        return "teaching-structure"
    if kind in {
        "graph-cycle",
        "state-truthfulness",
        "component-model",
        "flow-model",
        "framework-resolution",
        "actors-model",
        "events-model",
        "domain-model",
        "dependency-model",
    }:
        return "cross-artifact-consistency"
    if str(issue.get("section") or "") == "structure":
        return "artifact-structure"
    return "general"


def is_consistency_conflict(issue: dict) -> bool:
    return classify_issue_kind(issue) in {
        "graph-cycle",
        "state-truthfulness",
        "story-decomposition",
        "narrative-selection",
        "narrative-overview",
        "narrative-coherence",
        "narrative-count",
        "component-model",
        "flow-model",
        "concepts",
        "framework-resolution",
        "health-criteria-missing",
        "health-scenario-link-missing",
        "health-scenario-link-invalid",
        "health-ownership-unclear",
        "failure-scenario-missing",
        "health-model",
        "monitoring-model",
        "gaps-model",
        "actors-model",
        "events-model",
        "domain-model",
        "dependency-model",
    }


def issue_conflict_type(issue: dict) -> str | None:
    explicit = issue.get("conflict_type")
    if isinstance(explicit, str) and explicit:
        return explicit
    kind = classify_issue_kind(issue)
    mapping = {
        "graph-cycle": "cross_artifact",
        "state-truthfulness": "evidence_vs_model",
        "story-decomposition": "shape_tension",
        "narrative-selection": "cross_artifact",
        "narrative-overview": "cross_artifact",
        "narrative-coherence": "cross_artifact",
        "narrative-count": "shape_tension",
        "component-model": "cross_artifact",
        "flow-model": "cross_artifact",
        "concepts": "evidence_vs_model",
        "framework-resolution": "evidence_vs_model",
        "health-criteria-missing": "cross_artifact",
        "health-scenario-link-missing": "evidence_vs_model",
        "health-scenario-link-invalid": "cross_artifact",
        "health-ownership-unclear": "shape_tension",
        "failure-scenario-missing": "evidence_vs_model",
        "health-model": "cross_artifact",
        "monitoring-model": "cross_artifact",
        "gaps-model": "cross_artifact",
        "actors-model": "evidence_vs_model",
        "events-model": "evidence_vs_model",
        "domain-model": "evidence_vs_model",
        "dependency-model": "cross_artifact",
    }
    return mapping.get(kind)


def issue_priority(issue: dict) -> str:
    if str(issue.get("level") or "") == "ERROR":
        return "high"
    kind = classify_issue_kind(issue)
    if kind in {
        "graph-cycle",
        "state-truthfulness",
        "component-model",
        "flow-model",
        "path-provenance",
        "concepts",
        "health-model",
        "dependency-model",
        "monitoring-model",
        "gaps-model",
        "health-scenario-link-invalid",
    }:
        return "high"
    if kind in {
        "framework-resolution",
        "health-criteria-missing",
        "health-scenario-link-missing",
        "health-ownership-unclear",
        "failure-scenario-missing",
        "actors-model",
        "events-model",
        "domain-model",
    }:
        return "medium"
    if kind in {
        "story-decomposition",
        "narrative-selection",
        "narrative-overview",
        "narrative-coherence",
        "narrative-count",
        "story-quality",
    }:
        return "medium"
    return "low"


def recommended_artifacts(issue: dict) -> list[str]:
    kind = classify_issue_kind(issue)
    mapping = {
        "grounding": ["facts/symbols-seed.json"],
        "state-truthfulness": ["facts/state-seeds.json"],
        "story-decomposition": [
            "derived/story-seeds.json",
            "derived/component-seeds.json",
            "derived/narrative-seeds.json",
            "facts/state-access-summary.json",
        ],
        "narrative-selection": [
            "derived/story-seeds.json",
            "derived/component-seeds.json",
            "derived/narrative-seeds.json",
            "facts/control-hotspots.json",
            "facts/state-access-summary.json",
            "atlas.json",
        ],
        "narrative-overview": [
            "derived/story-seeds.json",
            "derived/component-seeds.json",
            "derived/narrative-seeds.json",
            "facts/control-hotspots.json",
            "atlas.json",
        ],
        "narrative-coherence": [
            "derived/story-seeds.json",
            "derived/component-seeds.json",
            "derived/narrative-seeds.json",
            "narratives.yaml",
            "atlas.json",
        ],
        "narrative-count": ["derived/narrative-seeds.json", "narratives.yaml", "atlas.json"],
        "story-quality": ["derived/story-seeds.json", "derived/component-seeds.json"],
        "component-model": ["derived/component-seeds.json", "derived/story-seeds.json"],
        "flow-model": ["facts/symbols-seed.json", "derived/component-seeds.json"],
        "health-criteria-missing": ["facts/health-candidates.json", "atlas.json"],
        "health-scenario-link-missing": ["facts/failure-scenario-candidates.json", "atlas.json"],
        "health-scenario-link-invalid": ["atlas.json", "facts/failure-scenario-candidates.json"],
        "health-ownership-unclear": ["derived/component-seeds.json", "atlas.json"],
        "failure-scenario-missing": [
            "facts/failure-scenario-candidates.json",
            "facts/health-candidates.json",
            "atlas.json",
        ],
        "health-model": ["facts/health-candidates.json", "atlas.json"],
        "monitoring-model": [
            "facts/health-candidates.json",
            "facts/failure-scenario-candidates.json",
            "atlas.json",
        ],
        "gaps-model": [
            "facts/health-candidates.json",
            "facts/failure-scenario-candidates.json",
            "facts/concepts.json",
            "atlas.json",
        ],
        "actors-model": ["facts/routes.json", "facts/jobs.json", "facts/events.json", "atlas.json"],
        "events-model": ["facts/events.json", "atlas.json"],
        "domain-model": ["facts/models.json", "atlas.json"],
        "dependency-model": ["facts/external-clients.json", "atlas.json"],
        "concepts": ["facts/concepts.json"],
        "framework-resolution": ["facts/frameworks.json"],
        "path-provenance": ["index.json", "startup.json"],
    }
    return mapping.get(kind, [])


def summarize_issues(issues: list[dict]) -> dict:
    by_level = Counter(str(issue.get("level") or "") for issue in issues)
    by_kind = Counter(classify_issue_kind(issue) for issue in issues)
    by_family = Counter(issue_family(issue) for issue in issues)
    consistency_conflicts = sum(1 for issue in issues if is_consistency_conflict(issue))
    return {
        "by_level": dict(sorted(by_level.items())),
        "by_kind": dict(sorted(by_kind.items())),
        "by_family": dict(sorted(by_family.items())),
        "consistency_conflict_count": consistency_conflicts,
    }


def suggested_resolution(issue: dict) -> str:
    kind = classify_issue_kind(issue)
    suggestions = {
        "path-provenance": "Correct the referenced repo or run path so it points to a real file or directory.",
        "grounding": "Tighten the claim so it uses code-shaped terms from the grounded snippet.",
        "story-decomposition": "Split the root into distinct concern-focused child stories or merge the weak child back, using deterministic story and narrative seeds as ranking hints.",
        "narrative-selection": "Swap in the smallest set of more explanatory stories, especially child, flow-bearing, or boundary stories suggested by deterministic narrative seeds.",
        "narrative-overview": "Rewrite the overview as a compact architectural synopsis that teaches system shape plus the operating model instead of cataloging components.",
        "narrative-coherence": "Rewrite the teaching goals, throughline, and story order so the narrative reads like one coherent lesson anchored in atlas structure and deterministic narrative seeds.",
        "narrative-count": "Reduce or add narratives until the repo has a small set of clearly distinct teaching paths rather than one overloaded path or many redundant ones.",
        "graph-cycle": "Revisit dependency direction and remove cyclic component relationships.",
        "state-truthfulness": "Widen the state label or persistence mode so it matches the configured backend reality.",
        "concepts": "Repair the concept evidence files or component references so provenance is valid.",
        "framework-resolution": "Reconcile the resolved framework summary with deterministic framework evidence and repo code.",
        "health-criteria-missing": "Add 1-3 concrete health.criteria statements that say what healthy operation looks like for this unit or flow.",
        "health-scenario-link-missing": "Link this unit to the shared failure scenarios it can trigger or participates in, rather than hiding that relationship elsewhere.",
        "health-scenario-link-invalid": "Fix the scenario refs so they only point at shared failure scenarios that actually start at or involve this unit.",
        "health-ownership-unclear": "Move child-local failures down to the specific child component unless this is truly a parent-level capability health condition.",
        "failure-scenario-missing": "Add a top-level failure_scenarios entry when deterministic evidence suggests a real multi-unit cascade.",
        "health-model": "Reshape the health block so it contains only criteria plus shared failure-scenario refs.",
        "monitoring-model": "Move observability details into top-level monitoring entries grounded in the components, flows, dependencies, or failure scenarios they cover.",
        "gaps-model": "Move missing monitoring, resilience, concept, or anti-pattern deficiencies into the top-level gaps list with clear affected ids and recommendations.",
        "component-model": "Refine the component graph so ids, parents, dependencies, and module paths are truthful.",
        "flow-model": "Tighten the flow description, references, or grounding so it matches the implementation path.",
        "actors-model": "Add grounded actors only when the repo shows real callers, schedulers, or event sources worth naming.",
        "events-model": "Add only the event boundaries that are grounded in facts and useful to understanding the architecture.",
        "domain-model": "Add a grounded domain model only if the repo exposes stable business entities, schemas, or bounded contexts worth naming.",
        "dependency-model": "Explain what this dependency provides to the system, which components or flows rely on it, and why it matters here.",
        "story-quality": "Narrow the story to a clearer concern and ground it with more precise evidence.",
        "general": "Re-read the referenced code and adjust the artifact until the validator no longer reports the issue.",
    }
    return suggestions.get(kind, suggestions["general"])


def build_repair_targets(issues: list[dict]) -> list[dict]:
    grouped: dict[str, dict] = {}
    for issue in issues:
        group_label = grounding_group_label(issue)
        if group_label:
            key = f"grounding::{issue.get('section')}::{group_label}"
            display = group_label
        else:
            key = stable_issue_id(issue)
            display = str(issue.get("message") or "")
        bucket = grouped.setdefault(
            key,
            {
                "id": key,
                "priority": issue_priority(issue),
                "family": issue_family(issue),
                "kind": classify_issue_kind(issue),
                "label": display,
                "issue_ids": [],
                "issue_count": 0,
                "sections": set(),
                "messages": [],
                "related_entities": set(),
                "evidence_refs": set(),
                "suggested_resolution": suggested_resolution(issue),
            },
        )
        bucket["issue_ids"].append(stable_issue_id(issue))
        bucket["issue_count"] += 1
        bucket["sections"].add(str(issue.get("section") or ""))
        bucket["messages"].append(str(issue.get("message") or ""))
        bucket["related_entities"].update(str(value) for value in (issue.get("related_entities") or []))
        bucket["evidence_refs"].update(str(value) for value in (issue.get("evidence_refs") or []))
        priorities = {"high": 3, "medium": 2, "low": 1}
        if priorities[issue_priority(issue)] > priorities[bucket["priority"]]:
            bucket["priority"] = issue_priority(issue)
    result = []
    for item in grouped.values():
        sections = sorted(section for section in item["sections"] if section)
        result.append(
            {
                "id": item["id"],
                "priority": item["priority"],
                "family": item["family"],
                "kind": item["kind"],
                "label": item["label"],
                "issue_count": item["issue_count"],
                "sections": sections,
                "related_entities": sorted(item["related_entities"]),
                "evidence_refs": sorted(item["evidence_refs"]),
                "issue_ids": item["issue_ids"],
                "messages": item["messages"],
                "recommended_artifacts": sorted(
                    {
                        artifact
                        for issue in issues
                        if stable_issue_id(issue) in item["issue_ids"]
                        for artifact in recommended_artifacts(issue)
                    }
                ),
                "suggested_resolution": item["suggested_resolution"],
            }
        )
    return result


def load_validation_history(path: Path) -> dict:
    if not path.exists():
        return {"version": "1", "log_type": "validation", "iterations": []}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(payload, dict) and isinstance(payload.get("iterations"), list):
            payload.setdefault("version", "1")
            payload.setdefault("log_type", "validation")
            return payload
    except json.JSONDecodeError:
        pass
    return {"version": "1", "log_type": "validation", "iterations": []}


def append_validation_history(
    path: Path, analysis_dir: Path, valid: bool, issues: list[dict]
) -> None:
    payload = load_validation_history(path)
    iterations = payload.setdefault("iterations", [])
    previous = iterations[-1] if iterations else {}
    previous_open = {
        item.get("id"): item
        for item in previous.get("issues", []) or []
        if item.get("status") in {"open", "unchanged", "regressed"}
    }
    previous_resolved_ids = {
        item.get("id")
        for iteration in iterations
        for item in iteration.get("resolved_issues", []) or []
        if item.get("id")
    }

    current_items = []
    current_issue_ids: set[str] = set()
    for issue in issues:
        issue_id = stable_issue_id(issue)
        current_issue_ids.add(issue_id)
        if issue_id in previous_open:
            status = "unchanged"
            first_seen = previous_open[issue_id].get("first_seen_iteration") or (
                len(iterations) or 1
            )
        elif issue_id in previous_resolved_ids:
            status = "regressed"
            first_seen = len(iterations) + 1
        else:
            status = "open"
            first_seen = len(iterations) + 1
        current_items.append(
            {
                "id": issue_id,
                "level": str(issue.get("level") or ""),
                "section": str(issue.get("section") or ""),
                "kind": classify_issue_kind(issue),
                "family": issue_family(issue),
                "priority": issue_priority(issue),
                "is_consistency_conflict": is_consistency_conflict(issue),
                "conflict_type": issue_conflict_type(issue),
                "message": str(issue.get("message") or ""),
                "related_entities": list(issue.get("related_entities") or []),
                "evidence_refs": list(issue.get("evidence_refs") or []),
                "related_issue_ids": list(issue.get("related_issue_ids") or []),
                "recommended_artifacts": recommended_artifacts(issue),
                "status": status,
                "first_seen_iteration": first_seen,
                "last_seen_iteration": len(iterations) + 1,
                "suggested_resolution": suggested_resolution(issue),
            }
        )

    resolved_items = []
    for issue_id, prior in previous_open.items():
        if issue_id in current_issue_ids:
            continue
        resolved_items.append(
            {
                "id": issue_id,
                "level": prior.get("level"),
                "section": prior.get("section"),
                "kind": prior.get("kind"),
                "family": prior.get("family"),
                "priority": prior.get("priority"),
                "is_consistency_conflict": prior.get("is_consistency_conflict", False),
                "conflict_type": prior.get("conflict_type"),
                "message": prior.get("message"),
                "related_entities": list(prior.get("related_entities") or []),
                "evidence_refs": list(prior.get("evidence_refs") or []),
                "related_issue_ids": list(prior.get("related_issue_ids") or []),
                "recommended_artifacts": list(prior.get("recommended_artifacts") or []),
                "status": "resolved",
                "first_seen_iteration": prior.get("first_seen_iteration"),
                "last_seen_iteration": len(iterations) + 1,
                "resolution_summary": "Issue no longer reported by the validator in this iteration.",
                "suggested_resolution": prior.get("suggested_resolution"),
            }
        )

    summary = summarize_issues(issues)
    priority_summary = {
        "high": sum(1 for issue in issues if issue_priority(issue) == "high"),
        "medium": sum(1 for issue in issues if issue_priority(issue) == "medium"),
        "low": sum(1 for issue in issues if issue_priority(issue) == "low"),
    }
    conflict_summary = {
        "open_consistency_conflicts": sum(1 for issue in issues if is_consistency_conflict(issue)),
        "by_conflict_type": dict(
            sorted(
                Counter(
                    issue_conflict_type(issue)
                    for issue in issues
                    if issue_conflict_type(issue)
                ).items()
            )
        ),
    }
    repair_targets = build_repair_targets(issues)
    quality_gate_reasons = [
        reason
        for reason, triggered in (
            ("medium_priority_issues_remaining", priority_summary["medium"] > 0),
            ("high_priority_issues_remaining", priority_summary["high"] > 0),
            ("consistency_conflicts_remaining", conflict_summary["open_consistency_conflicts"] > 0),
            (
                "warning_volume_still_actionable",
                sum(1 for issue in issues if issue.get("level") == "WARNING") > 5
                and len(repair_targets) <= 5,
            ),
        )
        if triggered
    ]
    iteration = {
        "iteration": len(iterations) + 1,
        "timestamp": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "status": "needs_refinement"
        if valid and quality_gate_reasons
        else ("valid" if valid else "invalid"),
        "error_count": sum(1 for issue in issues if issue.get("level") == "ERROR"),
        "warning_count": sum(1 for issue in issues if issue.get("level") == "WARNING"),
        "summary": summary,
        "priority_summary": priority_summary,
        "conflict_summary": conflict_summary,
        "repair_targets": repair_targets,
        "quality_gate": {
            "passed": valid and not quality_gate_reasons,
            "failure_reasons": quality_gate_reasons,
        },
        "issues": current_items,
        "resolved_issues": resolved_items,
    }
    iterations.append(iteration)
    payload["analysis_dir"] = str(analysis_dir)
    payload["latest_status"] = iteration["status"]
    payload["latest_iteration"] = iteration["iteration"]
    payload["updated_at"] = iteration["timestamp"]
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
