"""Shared validation for `health` blocks attached to atlas entities.

This logic is reused by components, flows, and external dependencies so the
health contract stays consistent across atlas sections.
"""

import json
from pathlib import Path

def validate_health(
    health: dict | None,
    section: str,
    item_id: str,
    *,
    valid_failure_scenario_ids: set[str] | None = None,
    candidate_failure_scenarios: list[dict] | None = None,
    starts_failure_scenarios: set[str] | None = None,
    involves_failure_scenarios: set[str] | None = None,
    project_root: Path | None = None,
    analysis_dir: Path | None = None,
) -> list[dict]:
    issues = []
    if not isinstance(health, dict):
        if candidate_failure_scenarios:
            issues.append({
                "level": "WARNING",
                "section": section,
                "kind": "health-scenario-link-missing",
                "message": f"'{item_id}' has no health block even though deterministic evidence suggests it participates in a shared failure scenario",
                "conflict_type": "evidence_vs_model",
                "related_entities": [item_id, *[str(candidate.get('id') or '') for candidate in candidate_failure_scenarios[:2]]],
                "evidence_refs": [str(ref) for candidate in candidate_failure_scenarios for ref in (candidate.get("evidence_refs") or [])[:1]][:3],
            })
        return issues

    criteria = health.get("criteria")
    if criteria is not None and not isinstance(criteria, list):
        issues.append({"level": "ERROR", "section": section, "kind": "health-model", "message": f"'{item_id}' health.criteria must be a list"})
        criteria = []
    triggers_failure_scenarios = health.get("triggers_failure_scenarios")
    if triggers_failure_scenarios is not None and not isinstance(triggers_failure_scenarios, list):
        issues.append({"level": "ERROR", "section": section, "kind": "health-model", "message": f"'{item_id}' health.triggers_failure_scenarios must be a list"})
        triggers_failure_scenarios = []
    participates_in_failure_scenarios = health.get("participates_in_failure_scenarios")
    if participates_in_failure_scenarios is not None and not isinstance(participates_in_failure_scenarios, list):
        issues.append({"level": "ERROR", "section": section, "kind": "health-model", "message": f"'{item_id}' health.participates_in_failure_scenarios must be a list"})
        participates_in_failure_scenarios = []
    valid_failure_scenario_ids = valid_failure_scenario_ids or set()
    trigger_ids = [str(item) for item in (triggers_failure_scenarios or []) if str(item or "").strip()]
    participant_ids = [str(item) for item in (participates_in_failure_scenarios or []) if str(item or "").strip()]
    for scenario_id in trigger_ids + participant_ids:
        if valid_failure_scenario_ids and scenario_id not in valid_failure_scenario_ids:
            issues.append({
                "level": "ERROR",
                "section": section,
                "kind": "health-model",
                "message": f"'{item_id}' health references unknown failure scenario '{scenario_id}'",
                "related_entities": [item_id, scenario_id],
            })
    for deprecated_field in ("signals", "related_failure_scenarios", "local", "integration", "propagation", "gaps", "failure_modes"):
        if deprecated_field in health:
            issues.append({
                "level": "ERROR",
                "section": section,
                "kind": "health-model",
                "message": f"'{item_id}' health.{deprecated_field} is deprecated in atlas v4; move monitoring, failure, and gap content to the top-level sections",
                "related_entities": [item_id],
            })
    criteria_values = [str(item) for item in (criteria or []) if str(item or "").strip()]
    if not criteria_values:
        issues.append({
            "level": "WARNING",
            "section": section,
            "kind": "health-criteria-missing",
            "message": f"'{item_id}' health is missing criteria; say what healthy operation looks like before describing failure",
            "related_entities": [item_id],
        })
    elif len(criteria_values) > 4:
        issues.append({
            "level": "WARNING",
            "section": section,
            "kind": "health-model",
            "message": f"'{item_id}' health.criteria is too long; keep it to roughly 1-4 concrete conditions",
            "related_entities": [item_id],
        })
    candidate_failure_scenarios = candidate_failure_scenarios or []
    starts_failure_scenarios = starts_failure_scenarios or set()
    involves_failure_scenarios = involves_failure_scenarios or set()

    for scenario_id in trigger_ids:
        if starts_failure_scenarios and scenario_id not in starts_failure_scenarios:
            issues.append({
                "level": "WARNING",
                "section": section,
                "kind": "health-scenario-link-invalid",
                "message": f"'{item_id}' claims it triggers failure scenario '{scenario_id}', but that scenario does not start at this unit",
                "conflict_type": "cross_artifact",
                "related_entities": [item_id, scenario_id],
            })
    for scenario_id in participant_ids:
        if involves_failure_scenarios and scenario_id not in involves_failure_scenarios:
            issues.append({
                "level": "WARNING",
                "section": section,
                "kind": "health-scenario-link-invalid",
                "message": f"'{item_id}' claims it participates in failure scenario '{scenario_id}', but that scenario does not involve this unit",
                "conflict_type": "cross_artifact",
                "related_entities": [item_id, scenario_id],
            })
    if starts_failure_scenarios and not set(trigger_ids).intersection(starts_failure_scenarios):
        issues.append({
            "level": "WARNING",
            "section": section,
            "kind": "health-scenario-link-missing",
            "message": f"'{item_id}' can trigger a shared failure scenario but health.triggers_failure_scenarios does not record it",
            "conflict_type": "cross_artifact",
            "related_entities": [item_id, *sorted(starts_failure_scenarios)[:2]],
        })
    missing_participation = involves_failure_scenarios.difference(starts_failure_scenarios).difference(set(participant_ids))
    if missing_participation:
        issues.append({
            "level": "WARNING",
            "section": section,
            "kind": "health-scenario-link-missing",
            "message": f"'{item_id}' participates in shared failure scenarios but health.participates_in_failure_scenarios does not record them",
            "conflict_type": "cross_artifact",
            "related_entities": [item_id, *sorted(missing_participation)[:2]],
        })
    if candidate_failure_scenarios and not (trigger_ids or participant_ids):
        issues.append({
            "level": "WARNING",
            "section": section,
            "kind": "health-scenario-link-missing",
            "message": f"'{item_id}' participates in a likely shared failure scenario but does not reference it from health",
            "conflict_type": "evidence_vs_model",
            "related_entities": [item_id, *[str(candidate.get('id') or '') for candidate in candidate_failure_scenarios[:2]]],
            "evidence_refs": [str(ref) for candidate in candidate_failure_scenarios for ref in (candidate.get("evidence_refs") or [])[:1]][:3],
        })
    return issues
