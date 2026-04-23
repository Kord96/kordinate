"""Validate `atlas.json`.

Checks owned here:
- top-level atlas required fields and version
- component ids, parent/child structure, and module grounding
- flows, steps, state, dependencies, frameworks, actors, events, and domain model
- concepts, tensions, monitoring, failure scenarios, and gaps
- health block references via `validate_health()`

This module is the authoritative checker for atlas.json; it does not inspect
story YAML, narratives.yaml, or meta.json.
"""

import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any

from .constants import REQUIRED_ATLAS_FIELDS
from .helpers import (
    check_existing_paths,
    check_grounded_in,
    kebab_case,
    validate_evidence_file,
    verify_grounding_quality,
)
from .atlas_health import validate_health

def validate_atlas(
    atlas: dict,
    project_root: Path | None = None,
    analysis_dir: Path | None = None,
    concepts_payload: dict | None = None,
    frameworks_payload: dict | None = None,
    health_candidates_payload: dict | None = None,
) -> list[dict]:
    issues = []

    def error(msg, section=""):
        issues.append({"level": "ERROR", "section": section, "message": msg})

    def warn(msg, section=""):
        issues.append({"level": "WARNING", "section": section, "message": msg})

    def state_semantic_warnings(state: dict) -> list[str]:
        warnings: list[str] = []
        sid = str(state.get("id") or "?")
        concept = str(state.get("concept") or "").lower()
        technology = str(state.get("technology") or "").lower()
        persistence = str(state.get("persistence") or "").lower()

        mentions_sql = any(token in technology for token in ("sql", "postgres", "mysql", "sqlite", "mariadb", "cockroach", "yugabyte", "sqlserver"))
        mentions_nosql = any(token in technology for token in ("nosql", "mongodb", "dynamodb", "cassandra", "arangodb", "couchbase", "document"))
        mentions_database = "database" in technology or "db-backed" in technology or "database-backed" in technology
        mentions_redis = "redis" in technology
        mentions_memory = "in-memory" in technology or "in memory" in technology

        if concept == "relational-db" and (mentions_nosql or ("sql" in technology and "nosql" in technology)):
            warnings.append(f"State '{sid}' concept 'relational-db' looks too narrow for the described technology '{state.get('technology')}'")
        if concept in {"document-store", "cache", "in-memory"} and mentions_sql and mentions_nosql:
            warnings.append(f"State '{sid}' concept '{concept}' looks too narrow for the described technology '{state.get('technology')}'")
        if persistence == "ephemeral" and (mentions_database or mentions_sql or mentions_nosql):
            warnings.append(f"State '{sid}' persistence 'ephemeral' may be inaccurate for a database-backed or durable-capable technology")
        if persistence == "persistent" and mentions_memory and not (mentions_redis or mentions_database or mentions_sql or mentions_nosql):
            warnings.append(f"State '{sid}' persistence 'persistent' may be inaccurate for an in-memory technology")
        if persistence in {"persistent", "ephemeral"} and mentions_redis and mentions_memory and (mentions_database or mentions_sql or mentions_nosql):
            warnings.append(f"State '{sid}' may need persistence 'mixed' because the technology describes multiple backend modes")
        return warnings

    def usefulness_tokens_present(text: str, tokens: set[str]) -> bool:
        lowered = text.lower()
        return any(token in lowered for token in tokens)

    def read_fact_domain(name: str) -> list[dict]:
        if not analysis_dir:
            return []
        path = analysis_dir / "facts" / f"{name}.json"
        if not path.exists():
            return []
        try:
            payload = json.loads(path.read_text())
        except json.JSONDecodeError:
            return []
        return [item for item in (payload.get("facts") or []) if isinstance(item, dict)]

    route_facts = read_fact_domain("routes")
    job_facts = read_fact_domain("jobs")
    event_facts = read_fact_domain("events")
    model_facts = read_fact_domain("models")
    optional_expectations = {
        "actors": bool(route_facts or job_facts or event_facts),
        "events": bool(event_facts),
        "domain_model": bool(model_facts),
    }
    monitoring_cover_ids: dict[str, list[str]] = defaultdict(list)
    for entry in atlas.get("monitoring", []) or []:
        if not isinstance(entry, dict) or not entry.get("id"):
            continue
        for ref in entry.get("covers") or []:
            ref_str = str(ref or "").strip()
            if ref_str:
                monitoring_cover_ids[ref_str].append(str(entry.get("id")))
    gap_affect_ids: dict[str, list[str]] = defaultdict(list)
    for gap in atlas.get("gaps", []) or []:
        if not isinstance(gap, dict) or not gap.get("id"):
            continue
        for ref in gap.get("affects") or []:
            ref_str = str(ref or "").strip()
            if ref_str:
                gap_affect_ids[ref_str].append(str(gap.get("id")))

    # Required fields
    for field in REQUIRED_ATLAS_FIELDS:
        if field not in atlas:
            error(f"Missing required field: {field}", "atlas")

    # Version
    if atlas.get("version") != "4":
        error(f"Expected version '4', got '{atlas.get('version')}'", "atlas")

    # Components
    components = atlas.get("components", [])
    if len(components) < 3:
        warn(f"Few components: {len(components)} (preferred range 5-10, but smaller focused repos may be valid)", "components")
    elif len(components) > 14:
        warn(f"Many components: {len(components)} (preferred range 5-10; ensure the architecture is not over-fragmented)", "components")

    component_ids = set()
    parent_of: dict[str, str] = {}
    child_links: dict[str, set[str]] = {}

    for component in components:
        cid = component.get("id", "")
        if not cid:
            error("Component missing id", "components")
            continue
        if not kebab_case(cid):
            error(f"Component ID not kebab-case: '{cid}'", "components")
        if cid in component_ids:
            error(f"Duplicate component ID: '{cid}'", "components")
        component_ids.add(cid)

    for component in components:
        cid = component.get("id", "")
        if not cid:
            continue
        parent = component.get("parent")
        if parent:
            if parent not in component_ids:
                error(f"Component '{cid}' references unknown parent '{parent}'", "components")
            elif parent == cid:
                error(f"Component '{cid}' cannot parent itself", "components")
            else:
                if cid in parent_of and parent_of[cid] != parent:
                    error(f"Component '{cid}' has conflicting parents '{parent_of[cid]}' and '{parent}'", "components")
                parent_of[cid] = parent
                child_links.setdefault(parent, set()).add(cid)
        for child in component.get("children", []) or []:
            if child not in component_ids:
                error(f"Component '{cid}' lists unknown child '{child}'", "components")
            elif child == cid:
                error(f"Component '{cid}' cannot list itself as child", "components")
            else:
                child_links.setdefault(cid, set()).add(child)
                if child in parent_of and parent_of[child] != cid:
                    error(f"Component '{child}' has conflicting parents '{parent_of[child]}' and '{cid}'", "components")
                parent_of[child] = cid
    if component_ids and not parent_of and len(component_ids) >= 4:
        error("Component hierarchy is fully flat. Use parent/child structure for real nested subsystems.", "components")

    root_components = [cid for cid in component_ids if cid not in parent_of]
    if len(root_components) < 2:
        error(f"Too few top-level components: {len(root_components)} (minimum 2)", "components")
    elif len(root_components) > 6:
        error(f"Too many top-level components: {len(root_components)} (maximum 6)", "components")
    elif len(root_components) not in {3, 4, 5}:
        warn(f"Top-level components count is {len(root_components)} (preferred range 3-5; use repo-shaped judgment)", "components")

    def compute_depth(cid: str, seen: set[str]) -> int:
        if cid in seen:
            error(f"Component hierarchy cycle detected at '{cid}'", "components")
            return 0
        parent = parent_of.get(cid)
        if not parent:
            return 1
        return 1 + compute_depth(parent, seen | {cid})

    for cid in component_ids:
        depth = compute_depth(cid, set())
        if depth > 3:
            warn(f"Component '{cid}' is at depth {depth} (preferred max 3)", "components")

    # All node IDs
    actor_ids = {a.get("id") for a in atlas.get("actors", [])}
    ext_dep_ids = {e.get("id") for e in atlas.get("external_dependencies", [])}
    state_ids = {s.get("id") for s in atlas.get("state", [])}
    flow_ids = {f.get("id") for f in atlas.get("flows", [])}
    failure_scenarios = atlas.get("failure_scenarios", [])
    if not isinstance(failure_scenarios, list):
        error("failure_scenarios must be a list", "failure_scenarios")
        failure_scenarios = []
    failure_scenario_ids = {
        str(item.get("id"))
        for item in failure_scenarios
        if isinstance(item, dict) and item.get("id")
    }
    failure_scenarios_by_start: dict[str, set[str]] = defaultdict(set)
    failure_scenarios_by_involved: dict[str, set[str]] = defaultdict(set)
    for scenario in failure_scenarios:
        if not isinstance(scenario, dict):
            continue
        scenario_id = str(scenario.get("id") or "").strip()
        if not scenario_id:
            continue
        for ref in [str(item) for item in (scenario.get("starts_at") or []) if str(item or "").strip()]:
            failure_scenarios_by_start[ref].add(scenario_id)
        for ref in [str(item) for item in (scenario.get("involves") or []) if str(item or "").strip()]:
            failure_scenarios_by_involved[ref].add(scenario_id)
    all_node_ids = component_ids | actor_ids | ext_dep_ids | state_ids
    all_health_target_ids = all_node_ids | flow_ids | failure_scenario_ids

    local_candidates_by_component: dict[str, list[dict]] = defaultdict(list)
    integration_candidates_by_source: dict[str, list[dict]] = defaultdict(list)
    propagation_candidates_by_source: dict[str, list[dict]] = defaultdict(list)
    failure_scenario_candidates_by_entity: dict[str, list[dict]] = defaultdict(list)
    if isinstance(health_candidates_payload, dict):
        for candidate in health_candidates_payload.get("local_candidates") or []:
            if isinstance(candidate, dict) and candidate.get("component"):
                local_candidates_by_component[str(candidate.get("component"))].append(candidate)
        for candidate in health_candidates_payload.get("integration_candidates") or []:
            if isinstance(candidate, dict) and candidate.get("source"):
                integration_candidates_by_source[str(candidate.get("source"))].append(candidate)
        for candidate in health_candidates_payload.get("propagation_candidates") or []:
            if isinstance(candidate, dict) and candidate.get("source"):
                propagation_candidates_by_source[str(candidate.get("source"))].append(candidate)

    failure_observations_payload = {}
    failure_observations_path = analysis_dir / "observations" / "failure-scenarios.json"
    if failure_observations_path.exists():
        try:
            failure_observations_payload = json.loads(failure_observations_path.read_text())
        except json.JSONDecodeError as e:
            issues.append({"level": "ERROR", "section": "failure-observations", "message": f"JSON parse error: {e}"})
    if isinstance(failure_observations_payload, dict):
        for observation in failure_observations_payload.get("observations") or []:
            if not isinstance(observation, dict):
                continue
            evidence = observation.get("evidence") if isinstance(observation.get("evidence"), dict) else {}
            starts_at = [str(item) for item in (evidence.get("starts_at") or []) if str(item or "").strip()]
            involves = [str(item) for item in (evidence.get("involves") or []) if str(item or "").strip()]
            for entity in starts_at + involves:
                failure_scenario_candidates_by_entity[entity].append(observation)

    # depends_on
    def check_deps(comps):
        for c in comps:
            for dep in c.get("depends_on", []):
                if dep not in component_ids:
                    error(f"Component '{c.get('id')}' depends_on unknown '{dep}'", "components")

    check_deps(components)

    for component in components:
        cid = str(component.get("id") or "?")
        component_children = [str(child) for child in (component.get("children") or []) if child]
        is_aggregate = bool(component_children)
        component_modules = [str(item) for item in (component.get("modules") or []) if item]
        dependency_targets = [str(item) for item in (component.get("depends_on") or []) if item]
        description = str(component.get("description") or "").strip()
        summary = str(component.get("summary") or "").strip()
        if not description:
            issues.append({
                "level": "WARNING",
                "section": "components",
                "kind": "component-model",
                "message": f"Component '{cid}' is missing description",
                "related_entities": [cid],
            })
        if not summary:
            issues.append({
                "level": "WARNING",
                "section": "components",
                "kind": "component-model",
                "message": f"Component '{cid}' is missing summary; add a 2-4 sentence architectural explanation for drilldown views",
                "related_entities": [cid],
            })
        else:
            summary_words = len(summary.split())
            if summary_words < 12:
                issues.append({
                    "level": "WARNING",
                    "section": "components",
                    "kind": "component-model",
                    "message": f"Component '{cid}' summary is too thin for drilldown; explain ownership, dependency shape, and why it matters",
                    "related_entities": [cid],
                })
            elif summary_words > 90:
                issues.append({
                    "level": "WARNING",
                    "section": "components",
                    "kind": "component-model",
                    "message": f"Component '{cid}' summary is too long; keep it to roughly 2-4 sentences",
                    "related_entities": [cid],
                })
        if not component_modules and not component_children:
            issues.append({
                "level": "WARNING",
                "section": "components",
                "kind": "component-model",
                "message": f"Component '{cid}' has neither modules nor children; ground it in code ownership or collapse it into a parent",
                "related_entities": [cid],
            })
        issues.extend(
            validate_health(
                component.get("health"),
                "components",
                cid or "<component>",
                valid_failure_scenario_ids=failure_scenario_ids,
                candidate_failure_scenarios=failure_scenario_candidates_by_entity.get(cid, []),
                starts_failure_scenarios=failure_scenarios_by_start.get(cid, set()),
                involves_failure_scenarios=failure_scenarios_by_involved.get(cid, set()),
                project_root=project_root,
                analysis_dir=analysis_dir,
            )
        )
        health = component.get("health") if isinstance(component.get("health"), dict) else {}
        criteria_values = [str(item) for item in ((health.get("criteria") or []) if isinstance(health, dict) else []) if str(item or "").strip()]
        trigger_refs = [str(item) for item in ((health.get("triggers_failure_scenarios") or []) if isinstance(health, dict) else []) if str(item or "").strip()]
        participant_refs = [str(item) for item in ((health.get("participates_in_failure_scenarios") or []) if isinstance(health, dict) else []) if str(item or "").strip()]

        if criteria_values and not any(any(token in criterion.lower() for token in ("serve", "load", "render", "return", "refresh", "persist", "update", "publish", "schedule", "sync", "accept", "respond", "hydrate", "compute", "classify", "route", "store")) for criterion in criteria_values):
            issues.append({
                "level": "WARNING",
                "section": "components",
                "kind": "health-criteria-missing",
                "message": f"Component '{cid}' health.criteria should describe concrete capability success, not only generic uptime",
                "related_entities": [cid],
            })
        if is_aggregate and criteria_values and not any(any(token in criterion.lower() for token in ("child", "subcomponent", "surface", "path", "capability", "slice", "pipeline", "service", "experience")) for criterion in criteria_values):
            issues.append({
                "level": "WARNING",
                "section": "components",
                "kind": "health-ownership-unclear",
                "message": f"Aggregate component '{cid}' health.criteria should describe the parent capability it owns, not only leaf mechanics",
                "related_entities": [cid],
            })
        if dependency_targets and not (trigger_refs or participant_refs):
            issues.append({
                "level": "WARNING",
                "section": "components",
                "kind": "health-scenario-link-missing",
                "message": f"Component '{cid}' depends on {', '.join(dependency_targets[:3])} but health does not link any shared failure scenario that explains how those seams degrade capability",
                "related_entities": [cid, *dependency_targets[:2]],
                "conflict_type": "cross_artifact",
            })
        candidate_health_signals = local_candidates_by_component.get(cid, []) + integration_candidates_by_source.get(cid, [])
        candidate_health_gaps = [candidate for candidate in candidate_health_signals if candidate.get("gaps")]
        if candidate_health_signals and not monitoring_cover_ids.get(cid):
            issues.append({
                "level": "WARNING",
                "section": "monitoring",
                "kind": "monitoring-model",
                "message": f"Component '{cid}' has deterministic health signals but no top-level monitoring entry covers it",
                "related_entities": [cid],
                "evidence_refs": [str(ref) for candidate in candidate_health_signals for ref in (candidate.get("evidence_refs") or [])[:1]][:3],
                "conflict_type": "evidence_vs_model",
            })
        if candidate_health_gaps and not gap_affect_ids.get(cid):
            issues.append({
                "level": "WARNING",
                "section": "gaps",
                "kind": "gaps-model",
                "message": f"Component '{cid}' has deterministic health or resilience gaps but no top-level gap entry affects it",
                "related_entities": [cid],
                "evidence_refs": [str(ref) for candidate in candidate_health_gaps for ref in (candidate.get("evidence_refs") or [])[:1]][:3],
                "conflict_type": "evidence_vs_model",
            })
        if component_modules and (project_root or analysis_dir):
            issues.extend(check_existing_paths(component_modules, project_root, analysis_dir, "components", cid, label="module"))

    depends_on_graph: dict[str, set[str]] = {
        str(component.get("id")): set(component.get("depends_on", []) or [])
        for component in components
        if component.get("id")
    }

    visited: set[str] = set()
    active: set[str] = set()

    def visit_dep(node: str, path: list[str]) -> None:
        if node in active:
            cycle_start = path.index(node) if node in path else 0
            cycle = path[cycle_start:] + [node]
            error(f"Component depends_on cycle detected: {' -> '.join(cycle)}", "components")
            return
        if node in visited:
            return
        visited.add(node)
        active.add(node)
        for dep in sorted(depends_on_graph.get(node, set())):
            if dep in depends_on_graph:
                visit_dep(dep, path + [dep])
        active.remove(node)

    for cid in sorted(depends_on_graph):
        visit_dep(cid, [cid])

    # Flows
    for f in atlas.get("flows", []):
        fid = f.get("id", "")
        description = str(f.get("description") or "").strip()
        summary = str(f.get("summary") or "").strip()
        trigger = str(f.get("trigger") or "").strip()
        outcome = str(f.get("outcome") or "").strip()
        if not description:
            warn(f"Flow '{fid}' is missing description", "flows")
        if not summary:
            warn(f"Flow '{fid}' is missing summary; add a 2-4 sentence explanation of the operating path", "flows")
        else:
            summary_words = len(summary.split())
            if summary_words < 12:
                warn(f"Flow '{fid}' summary is too thin for drilldown; explain the boundary crossings and why the path matters", "flows")
            elif summary_words > 90:
                warn(f"Flow '{fid}' summary is too long; keep it to roughly 2-4 sentences", "flows")
        if not trigger:
            warn(f"Flow '{fid}' is missing trigger; say what starts the path", "flows")
        if not outcome:
            warn(f"Flow '{fid}' is missing outcome; say what successful completion produces", "flows")
        elif len(outcome.split()) < 4:
            warn(f"Flow '{fid}' outcome is too thin; describe the result of the flow more clearly", "flows")
        if not f.get("grounded_in"):
            warn(f"Flow '{fid}' has no grounded_in", "flows")
        elif project_root or analysis_dir:
            issues.extend(check_grounded_in(f["grounded_in"], project_root, analysis_dir, "flows", fid))
            issues.extend(verify_grounding_quality(
                f["grounded_in"],
                " ".join(str(part) for part in (f.get("name"), f.get("title"), f.get("summary"), f.get("trigger"), f.get("outcome")) if part),
                project_root,
                analysis_dir,
                "flows",
                fid,
            ))
        issues.extend(
            validate_health(
                f.get("health"),
                "flows",
                fid or "<flow>",
                valid_failure_scenario_ids=failure_scenario_ids,
                candidate_failure_scenarios=failure_scenario_candidates_by_entity.get(fid, []),
                starts_failure_scenarios=failure_scenarios_by_start.get(fid, set()),
                involves_failure_scenarios=failure_scenarios_by_involved.get(fid, set()),
                project_root=project_root,
                analysis_dir=analysis_dir,
            )
        )
        for metric in f.get("business_metrics", []):
            if not isinstance(metric, dict):
                error(f"Flow '{fid}' business_metrics contains a non-object entry", "flows")
                continue
            if not metric.get("name"):
                error(f"Flow '{fid}' business metric is missing name", "flows")
            if not metric.get("description"):
                warn(f"Flow '{fid}' business metric '{metric.get('name', '?')}' has no description", "flows")
            if not metric.get("owner"):
                error(f"Flow '{fid}' business metric '{metric.get('name', '?')}' is missing owner", "flows")
            grounded = metric.get("grounded_in") or []
            if not grounded:
                warn(f"Flow '{fid}' business metric '{metric.get('name', '?')}' has no grounded_in", "flows")
            elif project_root or analysis_dir:
                issues.extend(check_grounded_in(grounded, project_root, analysis_dir, "flows", f"{fid}/{metric.get('name', '?')}"))
                issues.extend(verify_grounding_quality(
                    grounded,
                    " ".join(str(part) for part in (metric.get("name"), metric.get("description"), metric.get("owner")) if part),
                    project_root,
                    analysis_dir,
                    "flows",
                    f"{fid}/{metric.get('name', '?')}",
                ))
        steps = f.get("steps") or []
        if not isinstance(steps, list):
            error(f"Flow '{fid}' steps must be a list", "flows")
            steps = []
        if len(steps) < 2:
            warn(f"Flow '{fid}' should usually have at least 2 steps so the operating path is visible", "flows")
        boundary_crossings = 0
        output_like_steps = 0
        for idx, step in enumerate(steps, start=1):
            if not isinstance(step, dict):
                error(f"Flow '{fid}' step {idx} must be an object", "flows")
                continue
            if not str(step.get("component") or "").strip():
                error(f"Flow '{fid}' step {idx} is missing component", "flows")
            if not str(step.get("action") or "").strip():
                error(f"Flow '{fid}' step {idx} is missing action", "flows")
            for key in ("component", "to"):
                ref = step.get(key, "")
                if ref and ref not in all_node_ids:
                    error(f"Flow '{fid}' step {key} references unknown '{ref}'", "flows")
            source = str(step.get("component") or "").strip()
            target = str(step.get("to") or "").strip()
            if target and target != source:
                boundary_crossings += 1
            step_text = " ".join(str(step.get(key) or "") for key in ("action", "data", "transform", "to_state", "operation")).lower()
            if any(token in step_text for token in ("return", "render", "persist", "write", "store", "emit", "redirect", "deliver", "update", "clear", "set", "complete")):
                output_like_steps += 1
        if len(steps) >= 2 and boundary_crossings == 0:
            warn(f"Flow '{fid}' does not clearly cross a boundary or state handoff; tighten the path or split it into a more meaningful operating flow", "flows")
        health = f.get("health") if isinstance(f.get("health"), dict) else {}
        criteria_values = [str(item) for item in ((health.get("criteria") or []) if isinstance(health, dict) else []) if str(item or "").strip()]
        if criteria_values and not any(any(token in criterion.lower() for token in ("complete", "persist", "render", "redirect", "emit", "write", "load", "return", "update", "show", "store", "deliver")) for criterion in criteria_values):
            warn(f"Flow '{fid}' health.criteria should include at least one concrete success or completion condition", "flows")
        scenario_refs = [str(item) for item in ((health.get("triggers_failure_scenarios") or []) if isinstance(health, dict) else []) if str(item or "").strip()]
        scenario_refs += [str(item) for item in ((health.get("participates_in_failure_scenarios") or []) if isinstance(health, dict) else []) if str(item or "").strip()]
        if boundary_crossings > 1 and not scenario_refs:
            warn(f"Flow '{fid}' crosses multiple boundaries but health does not link a shared failure scenario for that operating path", "flows")
        if output_like_steps > 0 and not criteria_values:
            warn(f"Flow '{fid}' should state what successful completion looks like in health.criteria", "flows")
        if fid and f.get("business_metrics") and not monitoring_cover_ids.get(fid):
            issues.append({
                "level": "WARNING",
                "section": "monitoring",
                "kind": "monitoring-model",
                "message": f"Flow '{fid}' has business metrics but no top-level monitoring entry covers it",
                "related_entities": [fid],
                "conflict_type": "cross_artifact",
            })

    # State
    for s in atlas.get("state", []):
        sid = s.get("id", "")
        if not s.get("grounded_in"):
            warn(f"State '{sid}' has no grounded_in", "state")
        elif project_root or analysis_dir:
            issues.extend(check_grounded_in(s["grounded_in"], project_root, analysis_dir, "state", sid))
            issues.extend(verify_grounding_quality(
                s["grounded_in"],
                " ".join(
                    str(part)
                    for part in (
                        s.get("concept"),
                        s.get("technology"),
                        " ".join(str(item) for item in (s.get("stores") or []) if item),
                        s.get("purpose"),
                        s.get("component"),
                    )
                    if part
                ),
                project_root,
                analysis_dir,
                "state",
                sid,
            ))
        for key in ("component",):
            ref = s.get(key, "")
            if ref and ref not in all_node_ids:
                error(f"State '{sid}' {key} references unknown '{ref}'", "state")
        for r in s.get("readers", []):
            if r not in all_node_ids:
                error(f"State '{sid}' reader references unknown '{r}'", "state")
        for w in s.get("writers", []):
            if w not in all_node_ids:
                error(f"State '{sid}' writer references unknown '{w}'", "state")
        for message in state_semantic_warnings(s):
            warn(message, "state")

    # Conditional actors
    actors = atlas.get("actors", []) or []
    if optional_expectations["actors"] and not actors:
        issues.append({
            "level": "WARNING",
            "section": "actors",
            "kind": "actors-model",
            "message": "Script-derived route/job/event facts suggest the repo has meaningful actors, but atlas.actors is missing",
            "conflict_type": "evidence_vs_model",
            "evidence_refs": [*(str(f.get("source_files", [""])[0]) for f in route_facts[:1]), *(str(f.get("source_files", [""])[0]) for f in job_facts[:1]), *(str(f.get("source_files", [""])[0]) for f in event_facts[:1])][:3],
        })
    for actor in actors:
        if not isinstance(actor, dict):
            error("actors contains a non-object entry", "actors")
            continue
        aid = str(actor.get("id") or "")
        if not aid:
            error("actors entry is missing id", "actors")
            continue
        if not kebab_case(aid):
            error(f"Actor id not kebab-case: '{aid}'", "actors")
        actor_type = str(actor.get("type") or "").strip()
        if actor_type and actor_type not in {"user", "service", "cron", "cli", "data-source", "external"}:
            error(f"Actor '{aid}' has invalid type '{actor_type}'", "actors")
        if not str(actor.get("description") or "").strip():
            warn(f"Actor '{aid}' is missing description", "actors")

    # Conditional events
    events = atlas.get("events", []) or []
    if optional_expectations["events"] and not events:
        issues.append({
            "level": "WARNING",
            "section": "events",
            "kind": "events-model",
            "message": "Script-derived event facts suggest the repo has meaningful event boundaries, but atlas.events is missing",
            "conflict_type": "evidence_vs_model",
            "evidence_refs": [str(item) for fact in event_facts for item in (fact.get("source_files") or [])[:1]][:3],
        })
    for event in events:
        if not isinstance(event, dict):
            error("events contains a non-object entry", "events")
            continue
        eid = str(event.get("id") or "")
        if not eid:
            error("events entry is missing id", "events")
            continue
        if not kebab_case(eid):
            error(f"Event id not kebab-case: '{eid}'", "events")
        event_type = str(event.get("type") or "").strip()
        if event_type and event_type not in {"topic", "signal", "webhook", "cron", "pubsub"}:
            error(f"Event '{eid}' has invalid type '{event_type}'", "events")
        if not str(event.get("name") or "").strip():
            warn(f"Event '{eid}' is missing name", "events")
        producer = str(event.get("producer") or "").strip()
        if producer and producer not in all_node_ids:
            error(f"Event '{eid}' producer references unknown '{producer}'", "events")
        consumers = event.get("consumers") or []
        if not isinstance(consumers, list):
            error(f"Event '{eid}' consumers must be a list", "events")
            consumers = []
        for consumer in consumers:
            ref = str(consumer or "").strip()
            if ref and ref not in all_node_ids:
                error(f"Event '{eid}' consumer references unknown '{ref}'", "events")
        if not str(event.get("data") or "").strip():
            warn(f"Event '{eid}' is missing data summary", "events")

    # Conditional domain model
    domain_model = atlas.get("domain_model") or {}
    if optional_expectations["domain_model"] and not domain_model:
        issues.append({
            "level": "WARNING",
            "section": "domain_model",
            "kind": "domain-model",
            "message": "Script-derived model facts suggest the repo has a meaningful domain model, but atlas.domain_model is missing",
            "conflict_type": "evidence_vs_model",
            "evidence_refs": [str(item) for fact in model_facts for item in (fact.get("source_files") or [])[:1]][:3],
        })
    if domain_model:
        if not isinstance(domain_model, dict):
            error("domain_model must be an object", "domain_model")
        else:
            if not str(domain_model.get("primary") or "").strip():
                warn("domain_model.primary is missing or empty", "domain_model")
            if not str(domain_model.get("description") or "").strip():
                warn("domain_model.description is missing or empty", "domain_model")
            entities = domain_model.get("entities") or []
            relationships = domain_model.get("relationships") or []
            bounded_contexts = domain_model.get("bounded_contexts") or []
            if not entities and not relationships and not bounded_contexts:
                warn("domain_model is present but empty; either ground it with real entities or omit it", "domain_model")
            if bounded_contexts and not isinstance(bounded_contexts, list):
                error("domain_model.bounded_contexts must be a list", "domain_model")
                bounded_contexts = []
            for context in bounded_contexts:
                if not isinstance(context, dict):
                    error("domain_model.bounded_contexts contains a non-object entry", "domain_model")
                    continue
                cid = str(context.get("id") or "")
                if not cid:
                    error("domain_model bounded context is missing id", "domain_model")
                    continue
                if not str(context.get("name") or "").strip():
                    warn(f"Bounded context '{cid}' is missing name", "domain_model")
                if not str(context.get("description") or "").strip():
                    warn(f"Bounded context '{cid}' is missing description", "domain_model")
                modules = context.get("modules") or []
                if modules and (project_root or analysis_dir):
                    issues.extend(check_existing_paths(modules, project_root, analysis_dir, "domain_model", cid, label="module"))

    flow_ids = {f.get("id") for f in atlas.get("flows", []) if f.get("id")}
    state_ids = {s.get("id") for s in atlas.get("state", []) if s.get("id")}
    event_ids = {e.get("id") for e in atlas.get("events", []) if e.get("id")}

    concept_review_requirements: dict[str, dict] = {}
    if isinstance(concepts_payload, dict):
        for fact in concepts_payload.get("facts") or []:
            if not isinstance(fact, dict) or fact.get("kind") != "concept":
                continue
            raw = fact.get("raw_evidence") or {}
            concept_id = str(raw.get("concept_id") or "").strip()
            if not concept_id:
                continue
            review = raw.get("review") or {}
            questions = review.get("questions") or {}
            if not review.get("required"):
                continue
            concept_review_requirements[concept_id] = {
                "question_ids": list((questions.get("entry_ids") or [])),
                "detector_backing": str(raw.get("detector_backing") or ""),
            }

    # Concepts
    concepts = atlas.get("concepts", {})
    if concepts is None:
        concepts = {}
    elif not isinstance(concepts, dict):
        error("concepts must be an object with detected_patterns and detected_anti_patterns", "concepts")
        concepts = {}

    def validate_concept_entry(entry: dict, entry_kind: str) -> None:
        cid = str(entry.get("id") or "?")
        if not entry.get("summary"):
            warn(f"{entry_kind.title()} '{cid}' is missing repo-specific summary text", "concepts")
        if not entry.get("why_it_matters"):
            warn(f"{entry_kind.title()} '{cid}' is missing why_it_matters", "concepts")
        linked_components = [comp for comp in entry.get("components", []) if comp]
        linked_flows = [flow for flow in entry.get("flows", []) if flow]
        linked_state = [state_id for state_id in entry.get("state", []) if state_id]
        if not (linked_components or linked_flows or linked_state):
            warn(f"{entry_kind.title()} '{cid}' is not linked to any component, flow, or state", "concepts")
        for comp in linked_components:
            if comp not in all_node_ids:
                error(f"{entry_kind.title()} '{cid}' references unknown component '{comp}'", "concepts")
        for flow in linked_flows:
            if flow not in flow_ids:
                error(f"{entry_kind.title()} '{cid}' references unknown flow '{flow}'", "concepts")
        for state_id in linked_state:
            if state_id not in state_ids:
                error(f"{entry_kind.title()} '{cid}' references unknown state '{state_id}'", "concepts")
        grounded_refs = entry.get("grounded_in") or []
        raw_evidence = entry.get("evidence")
        evidence = raw_evidence if isinstance(raw_evidence, dict) else {}
        if raw_evidence not in (None, {}) and not isinstance(raw_evidence, dict):
            error(
                f"{entry_kind.title()} '{cid}' evidence must be an object, got {type(raw_evidence).__name__}",
                "concepts",
            )
        raw_files = evidence.get("files") or []
        if raw_files and not isinstance(raw_files, list):
            error(f"{entry_kind.title()} '{cid}' evidence.files must be a list", "concepts")
            files: list[str] = []
        else:
            files = [str(item) for item in raw_files if item]
        raw_questions = evidence.get("questions_asked") or []
        if raw_questions and not isinstance(raw_questions, list):
            error(f"{entry_kind.title()} '{cid}' evidence.questions_asked must be a list", "concepts")
            questions_asked: list[str] = []
        else:
            questions_asked = [str(item) for item in raw_questions if item]
        if not grounded_refs and not files:
            warn(f"{entry_kind.title()} '{cid}' has no grounded_in or evidence files", "concepts")
        if grounded_refs and (project_root or analysis_dir):
            issues.extend(check_grounded_in(grounded_refs, project_root, analysis_dir, "concepts", cid))
            issues.extend(verify_grounding_quality(
                grounded_refs,
                " ".join(
                    str(part)
                    for part in (
                        entry.get("summary"),
                        entry.get("why_it_matters"),
                        evidence.get("note"),
                    )
                    if part
                ),
                project_root,
                analysis_dir,
                "concepts",
                cid,
                evidence_snippet=str(evidence.get("note") or ""),
            ))
        if files and (project_root or analysis_dir):
            issues.extend(check_existing_paths(files, project_root, analysis_dir, "concepts", cid, label="evidence file"))
        review_requirement = concept_review_requirements.get(cid)
        if review_requirement:
            if not questions_asked:
                warn(
                    f"{entry_kind.title()} '{cid}' requires review by deterministic evidence but records no answered review questions",
                    "concepts",
                )
            elif review_requirement.get("question_ids"):
                missing = sorted(set(str(item) for item in review_requirement["question_ids"]) - set(questions_asked))
                if missing:
                    warn(
                        f"{entry_kind.title()} '{cid}' does not record all expected review questions from deterministic evidence: {', '.join(missing)}",
                        "concepts",
                    )

    for p in concepts.get("detected_patterns", []):
        validate_concept_entry(p, "pattern")
    for ap in concepts.get("detected_anti_patterns", []):
        validate_concept_entry(ap, "anti-pattern")

    metadata = atlas.get("metadata") or {}
    if metadata and not isinstance(metadata, dict):
        error("metadata must be an object", "metadata")
        metadata = {}

    framework_facts: dict[str, dict[str, Any]] = {}
    if isinstance(frameworks_payload, dict):
        for fact in frameworks_payload.get("facts") or []:
            if not isinstance(fact, dict) or fact.get("kind") != "framework":
                continue
            raw = fact.get("raw_evidence") or {}
            name = str(raw.get("framework") or raw.get("name") or "").strip()
            if not name:
                continue
            framework_facts[name] = fact

    if not metadata:
        issues.append({
            "level": "WARNING",
            "section": "metadata",
            "kind": "metadata",
            "message": "atlas.json is missing metadata; emit the resolved stack summary and run metadata when deterministic facts are available",
            "related_entities": [],
            "evidence_refs": ["index.json", "facts/frameworks.json"],
            "conflict_type": "evidence_vs_model",
        })
    if metadata:
        stack_summary = str(metadata.get("stack_summary") or "").strip()
        if not stack_summary:
            issues.append({
                "level": "WARNING",
                "section": "metadata",
                "kind": "metadata",
                "message": "metadata.stack_summary is missing or empty",
                "related_entities": [],
                "evidence_refs": ["index.json", "facts/frameworks.json"],
                "conflict_type": "evidence_vs_model",
            })
        languages = metadata.get("languages") or []
        if languages and not isinstance(languages, list):
            error("metadata.languages must be a list", "metadata")
        elif not languages:
            issues.append({
                "level": "WARNING",
                "section": "metadata",
                "kind": "metadata",
                "message": "metadata.languages is missing or empty",
                "related_entities": [],
                "evidence_refs": ["index.json", "facts/frameworks.json"],
                "conflict_type": "evidence_vs_model",
            })

        technologies = metadata.get("technologies") or []
        if technologies and not isinstance(technologies, list):
            error("metadata.technologies must be a list", "metadata")
        elif not technologies:
            issues.append({
                "level": "WARNING",
                "section": "metadata",
                "kind": "metadata",
                "message": "metadata.technologies is missing or empty",
                "related_entities": [],
                "evidence_refs": ["index.json", "facts/frameworks.json"],
                "conflict_type": "evidence_vs_model",
            })

        frameworks_meta = metadata.get("frameworks") or []
        if frameworks_meta and not isinstance(frameworks_meta, list):
            error("metadata.frameworks must be a list", "metadata")
            frameworks_meta = []

        framework_names_in_meta: set[str] = set()
        for item in frameworks_meta:
            if not isinstance(item, dict):
                error("metadata.frameworks contains a non-object entry", "metadata")
                continue
            name = str(item.get("name") or "").strip()
            if not name:
                error("metadata.frameworks entry is missing name", "metadata")
                continue
            framework_names_in_meta.add(name)
            if not item.get("status"):
                issues.append({
                    "level": "WARNING",
                    "section": "metadata",
                    "kind": "framework-resolution",
                    "message": f"metadata.frameworks entry '{name}' is missing resolution status",
                    "related_entities": [name],
                    "evidence_refs": [],
                    "conflict_type": "evidence_vs_model",
                })
            if framework_facts and name not in framework_facts:
                issues.append({
                    "level": "WARNING",
                    "section": "metadata",
                    "kind": "framework-resolution",
                    "message": f"metadata.frameworks includes '{name}' but deterministic framework facts do not support it in this run",
                    "related_entities": [name],
                    "evidence_refs": [],
                    "conflict_type": "evidence_vs_model",
                })

        for name, fact in framework_facts.items():
            confidence = str((fact.get("raw_evidence") or {}).get("confidence_hint") or "").lower()
            if confidence not in {"medium", "high"}:
                continue
            if name not in framework_names_in_meta:
                issues.append({
                    "level": "WARNING",
                    "section": "metadata",
                    "kind": "framework-resolution",
                    "message": f"Script-derived framework evidence suggests '{name}' but metadata.frameworks does not record a resolved entry",
                    "related_entities": [name],
                    "evidence_refs": list(fact.get("source_files") or [])[:3],
                    "conflict_type": "evidence_vs_model",
                })

    # Tensions
    for tension in atlas.get("tensions", []):
        for comp in tension.get("components", []):
            if comp not in all_node_ids:
                error(f"Tension '{tension.get('id', '?')}' references unknown component '{comp}'", "tensions")

    # External dependency health
    for dependency in atlas.get("external_dependencies", []):
        did = dependency.get("id", "")
        purpose = str(dependency.get("purpose") or "").strip()
        summary = str(dependency.get("summary") or "").strip()
        if not purpose:
            issues.append({
                "level": "WARNING",
                "section": "external_dependencies",
                "kind": "dependency-model",
                "message": f"External dependency '{did}' is missing purpose; explain what capability it provides here",
                "related_entities": [did],
            })
        elif len(purpose.split()) < 4:
            issues.append({
                "level": "WARNING",
                "section": "external_dependencies",
                "kind": "dependency-model",
                "message": f"External dependency '{did}' purpose is too thin; say why the system needs it, not just what it is",
                "related_entities": [did],
            })
        if not summary:
            issues.append({
                "level": "WARNING",
                "section": "external_dependencies",
                "kind": "dependency-model",
                "message": f"External dependency '{did}' is missing summary; add a 2-4 sentence explanation of what it provides and what relies on it",
                "related_entities": [did],
            })
        else:
            summary_words = len(summary.split())
            if summary_words < 12:
                issues.append({
                    "level": "WARNING",
                    "section": "external_dependencies",
                    "kind": "dependency-model",
                    "message": f"External dependency '{did}' summary is too thin for drilldown; explain the capability it provides and why it matters",
                    "related_entities": [did],
                })
            elif summary_words > 90:
                issues.append({
                    "level": "WARNING",
                    "section": "external_dependencies",
                    "kind": "dependency-model",
                    "message": f"External dependency '{did}' summary is too long; keep it to roughly 2-4 sentences",
                    "related_entities": [did],
                })
            detail_tokens = {"provides", "used", "relies", "depends", "backs", "stores", "publishes", "serves", "carries", "queues", "persists", "enables"}
            if not usefulness_tokens_present(summary, detail_tokens):
                issues.append({
                    "level": "WARNING",
                    "section": "external_dependencies",
                    "kind": "dependency-model",
                    "message": f"External dependency '{did}' summary should explain what capability it provides and which paths rely on it",
                    "related_entities": [did],
                })
        issues.extend(
            validate_health(
                dependency.get("health"),
                "external_dependencies",
                did or "<dependency>",
                valid_failure_scenario_ids=failure_scenario_ids,
                candidate_failure_scenarios=failure_scenario_candidates_by_entity.get(did, []),
                starts_failure_scenarios=failure_scenarios_by_start.get(did, set()),
                involves_failure_scenarios=failure_scenarios_by_involved.get(did, set()),
                project_root=project_root,
                analysis_dir=analysis_dir,
            )
        )
        if failure_scenario_candidates_by_entity.get(did, []) and not monitoring_cover_ids.get(did):
            issues.append({
                "level": "WARNING",
                "section": "monitoring",
                "kind": "monitoring-model",
                "message": f"External dependency '{did}' participates in likely shared failure scenarios but no top-level monitoring entry covers it",
                "related_entities": [did],
                "evidence_refs": [str(ref) for candidate in failure_scenario_candidates_by_entity.get(did, []) for ref in (candidate.get("evidence_refs") or [])[:1]][:3],
                "conflict_type": "evidence_vs_model",
            })

    monitoring_entries = atlas.get("monitoring", [])
    if not isinstance(monitoring_entries, list):
        error("monitoring must be a list", "monitoring")
        monitoring_entries = []
    seen_monitoring_ids: set[str] = set()
    for entry in monitoring_entries:
        if not isinstance(entry, dict):
            error("monitoring contains a non-object entry", "monitoring")
            continue
        mid = str(entry.get("id") or "").strip()
        if not mid:
            error("monitoring entry is missing id", "monitoring")
            continue
        if not kebab_case(mid):
            error(f"Monitoring id not kebab-case: '{mid}'", "monitoring")
        if mid in seen_monitoring_ids:
            error(f"Duplicate monitoring id '{mid}'", "monitoring")
        seen_monitoring_ids.add(mid)
        if not str(entry.get("name") or "").strip():
            warn(f"Monitoring entry '{mid}' is missing name", "monitoring")
        kind = str(entry.get("kind") or "").strip()
        if kind and kind not in {"signal", "metric", "alert", "dashboard", "trace"}:
            error(f"Monitoring entry '{mid}' has invalid kind '{kind}'", "monitoring")
        if not str(entry.get("summary") or "").strip():
            warn(f"Monitoring entry '{mid}' is missing summary", "monitoring")
        covers = [str(item) for item in (entry.get("covers") or []) if str(item or "").strip()]
        if not covers:
            warn(f"Monitoring entry '{mid}' should list covers ids", "monitoring")
        for ref in covers:
            if ref not in all_health_target_ids:
                error(f"Monitoring entry '{mid}' references unknown cover id '{ref}'", "monitoring")
        signals = entry.get("signals")
        if signals is not None and not isinstance(signals, list):
            error(f"Monitoring entry '{mid}' signals must be a list", "monitoring")
        grounded = entry.get("grounded_in") or []
        if not grounded:
            warn(f"Monitoring entry '{mid}' has no grounded_in", "monitoring")
        elif project_root or analysis_dir:
            issues.extend(check_grounded_in(grounded, project_root, analysis_dir, "monitoring", mid))

    # Shared failure scenarios
    seen_failure_scenario_ids: set[str] = set()
    for scenario in failure_scenarios:
        if not isinstance(scenario, dict):
            error("failure_scenarios contains a non-object entry", "failure_scenarios")
            continue
        sid = str(scenario.get("id") or "")
        if not sid:
            error("failure_scenarios entry is missing id", "failure_scenarios")
            continue
        if not kebab_case(sid):
            error(f"Failure scenario id not kebab-case: '{sid}'", "failure_scenarios")
        if sid in seen_failure_scenario_ids:
            error(f"Duplicate failure scenario id '{sid}'", "failure_scenarios")
        seen_failure_scenario_ids.add(sid)
        if not str(scenario.get("name") or "").strip():
            warn(f"Failure scenario '{sid}' is missing name", "failure_scenarios")
        scope = str(scenario.get("scope") or "").strip()
        if scope not in {"integration", "cascading"}:
            error(f"Failure scenario '{sid}' has invalid scope '{scope}'", "failure_scenarios")
        starts_at = [str(item) for item in (scenario.get("starts_at") or []) if str(item or "").strip()]
        involves = [str(item) for item in (scenario.get("involves") or []) if str(item or "").strip()]
        if not starts_at:
            error(f"Failure scenario '{sid}' must list starts_at ids", "failure_scenarios")
        if not involves:
            error(f"Failure scenario '{sid}' must list involves ids", "failure_scenarios")
        for ref in starts_at + involves:
            if ref not in all_health_target_ids:
                error(f"Failure scenario '{sid}' references unknown id '{ref}'", "failure_scenarios")
        chain = scenario.get("chain") or []
        if not isinstance(chain, list):
            error(f"Failure scenario '{sid}' chain must be a list", "failure_scenarios")
            chain = []
        chain_nodes: set[str] = set()
        for step in chain:
            if not isinstance(step, dict):
                error(f"Failure scenario '{sid}' chain contains a non-object entry", "failure_scenarios")
                continue
            from_id = str(step.get("from") or "")
            to_id = str(step.get("to") or "")
            effect = str(step.get("effect") or "").strip()
            if not from_id or not to_id or not effect:
                error(f"Failure scenario '{sid}' chain steps must include from, to, and effect", "failure_scenarios")
                continue
            chain_nodes.add(from_id)
            chain_nodes.add(to_id)
            if from_id not in all_health_target_ids:
                error(f"Failure scenario '{sid}' chain references unknown from id '{from_id}'", "failure_scenarios")
            if to_id not in all_health_target_ids:
                error(f"Failure scenario '{sid}' chain references unknown to id '{to_id}'", "failure_scenarios")
            if from_id in component_ids and to_id in component_ids:
                from_component = next((component for component in components if component.get("id") == from_id), {})
                to_component = next((component for component in components if component.get("id") == to_id), {})
                from_parent = str(from_component.get("parent") or "")
                to_parent = str(to_component.get("parent") or "")
                if (
                    to_id not in (from_component.get("depends_on") or [])
                    and from_id not in (to_component.get("depends_on") or [])
                    and from_parent != to_id
                    and to_parent != from_id
                    and (from_parent != to_parent or not from_parent)
                ):
                    warn(f"Failure scenario '{sid}' chain edge '{from_id}' -> '{to_id}' is not reflected in component depends_on or hierarchy; confirm the propagation path explicitly", "failure_scenarios")
        if len(involves) >= 2 and not chain:
            warn(f"Failure scenario '{sid}' should include a chain when it spans multiple units", "failure_scenarios")
        uncovered_involves = [ref for ref in involves if ref not in chain_nodes and ref not in starts_at]
        if uncovered_involves:
            warn(f"Failure scenario '{sid}' involves ids not touched by the chain: {', '.join(uncovered_involves[:3])}", "failure_scenarios")
        if not str(scenario.get("degraded_mode") or "").strip():
            warn(f"Failure scenario '{sid}' is missing degraded_mode", "failure_scenarios")
        if not any(isinstance(scenario.get(field), list) and scenario.get(field) for field in ("mitigations",)):
            warn(f"Failure scenario '{sid}' should include mitigations or containment guidance", "failure_scenarios")
        grounded = scenario.get("grounded_in") or []
        if not grounded:
            warn(f"Failure scenario '{sid}' has no grounded_in", "failure_scenarios")
        elif project_root or analysis_dir:
            issues.extend(check_grounded_in(grounded, project_root, analysis_dir, "failure_scenarios", sid))

    if isinstance(failure_observations_payload, dict):
        present_ids = seen_failure_scenario_ids
        for observation in failure_observations_payload.get("observations") or []:
            if not isinstance(observation, dict):
                continue
            observation_id = str(observation.get("id") or "")
            if not observation_id or observation_id in present_ids:
                continue
            evidence = observation.get("evidence") if isinstance(observation.get("evidence"), dict) else {}
            involves = [str(item) for item in (evidence.get("involves") or []) if str(item or "").strip()]
            if len(involves) < 2:
                continue
            issues.append({
                "level": "WARNING",
                "section": "failure_scenarios",
                "kind": "failure-scenario-missing",
                "message": f"Failure observation '{observation_id}' is not modeled in atlas.failure_scenarios",
                "conflict_type": "evidence_vs_model",
                "related_entities": [observation_id, *involves[:3]],
                "evidence_refs": [str(ref) for ref in (evidence.get("repo_refs") or [])[:3]],
            })

    concept_ids = {p.get("id") for p in concepts.get("detected_patterns", []) if p.get("id")}
    concept_ids |= {ap.get("id") for ap in concepts.get("detected_anti_patterns", []) if ap.get("id")}
    tension_ids = {t.get("id") for t in atlas.get("tensions", []) if t.get("id")}
    gap_entries = atlas.get("gaps", [])
    if not isinstance(gap_entries, list):
        error("gaps must be a list", "gaps")
        gap_entries = []
    seen_gap_ids: set[str] = set()
    valid_gap_target_ids = all_health_target_ids | concept_ids
    for gap in gap_entries:
        if not isinstance(gap, dict):
            error("gaps contains a non-object entry", "gaps")
            continue
        gid = str(gap.get("id") or "").strip()
        if not gid:
            error("gaps entry is missing id", "gaps")
            continue
        if not kebab_case(gid):
            error(f"Gap id not kebab-case: '{gid}'", "gaps")
        if gid in seen_gap_ids:
            error(f"Duplicate gap id '{gid}'", "gaps")
        seen_gap_ids.add(gid)
        if not str(gap.get("kind") or "").strip():
            warn(f"Gap '{gid}' is missing kind", "gaps")
        if not str(gap.get("title") or "").strip():
            warn(f"Gap '{gid}' is missing title", "gaps")
        if not str(gap.get("summary") or "").strip():
            warn(f"Gap '{gid}' is missing summary", "gaps")
        affects = [str(item) for item in (gap.get("affects") or []) if str(item or "").strip()]
        if not affects:
            warn(f"Gap '{gid}' should list affects ids", "gaps")
        for ref in affects:
            if ref not in valid_gap_target_ids:
                error(f"Gap '{gid}' references unknown affect id '{ref}'", "gaps")
        if not str(gap.get("recommendation") or "").strip():
            warn(f"Gap '{gid}' is missing recommendation", "gaps")
        grounded = gap.get("grounded_in") or []
        if grounded and (project_root or analysis_dir):
            issues.extend(check_grounded_in(grounded, project_root, analysis_dir, "gaps", gid))

    all_entity_ids = all_node_ids | flow_ids | event_ids | concept_ids | tension_ids | failure_scenario_ids | seen_gap_ids

    return issues, all_node_ids, all_entity_ids
