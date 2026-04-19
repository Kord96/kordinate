#!/usr/bin/env python3
"""Validate Augur analysis output for deterministic and semantic phases.

Usage:
    python validate_output.py <analysis-dir>

    <analysis-dir> is the validated Augur analysis directory.
    Deterministic-only runs must contain blast.json and facts/.
    Full semantic runs must also contain atlas.json, stories/, and narratives.yaml.
    meta.json is validated when present, but it may be finalized after semantic validation.
    e.g., /kord/augur/memory/projects/<project>/analysis/<sha>/<analysis-id>/

Lock management is automatic when VALIDATE_LOCK=1 is set in the environment.
This is used by the hook infrastructure, not by the agent directly.

Checks:
    Phase 1 deterministic:
        - blast.json exists and is valid JSON
        - facts/ exists and contains extracted domain files

    Phase 2 semantic (atlas v4):
        - atlas.json exists and is valid JSON
        - Required top-level fields present
        - Version is "4"
        - IDs are kebab-case and unique
        - All cross-references resolve
        - Top-level component count is 3-5
        - Component count is 5-10 (warning if outside 4-12)
        - grounded_in arrays present on flows, state, and attached health failure modes

    Phase 2 (stories):
        - narrative/stories/ directory exists
        - Each file is valid YAML
        - Required fields: id, title, summary
        - Summary word count <= 100
        - Bold refs in summary resolve to atlas node IDs
        - Structure/flow node refs resolve to atlas
        - Observations have grounded_in

    Phase 2 (narratives):
        - narratives.yaml exists
        - top-level version is "1"
        - system-overview narrative exists
        - Each narrative references existing story IDs
        - Narrative length is 3-8 stories

    Phase 2 (meta, optional during validation loop):
        - meta.json, when present, is valid JSON
        - core fields match meta-schema.md
        - artifact and schema paths are absolute

    Structure:
        - blast.json is JSON
        - atlas.json is JSON (not YAML)
        - stories/*.yaml are YAML (not .md or .json)
        - narratives.yaml is YAML

Exit codes:
    0 = valid (lock removed if --lock)
    1 = errors found (lock created if --lock)
    2 = directory not found or critical error
"""

import json
import os
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime, UTC
import hashlib
from pathlib import Path
from typing import Any, Iterable

try:
    import yaml
except ImportError:
    yaml = None

KEBAB_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")

REQUIRED_ATLAS_FIELDS = [
    "version", "generated", "project", "purpose",
    "components", "flows", "state",
    "external_dependencies", "failure_scenarios", "monitoring", "gaps", "concepts", "tensions"
]

CANONICAL_NARRATIVE_IDS = {
    "system-overview",
    "runtime-paths",
    "state-and-data",
    "integrations",
    "operations-and-failure",
    "extensibility",
    "security-and-access",
}

DETERMINISTIC_ONLY = (
    os.getenv("AUGUR_DETERMINISTIC_ONLY") in ("1", "true", "TRUE", "yes", "YES")
)


def kebab_case(s: str) -> bool:
    return bool(KEBAB_RE.match(s))


def normalize_rel_path(path: str) -> str:
    return str(path or "").split(":", 1)[0].strip()


def path_matches_prefix(path: str, prefix: str) -> bool:
    left = normalize_rel_path(path).rstrip("/")
    right = normalize_rel_path(prefix).rstrip("/")
    if not left or not right:
        return False
    return left == right or left.startswith(right + "/") or right.startswith(left + "/")


def check_grounded_in(
    refs: list,
    project_root: Path | None,
    analysis_dir: Path | None,
    section: str,
    item_id: str,
) -> list[dict]:
    """Verify grounded_in file:line references point to real files.

    References may resolve against:
    - the analyzed project root for repo files
    - the analysis directory for run artifacts such as facts/startup.json
    """
    issues = []
    for ref in refs:
        filepath = ref.split(":")[0]
        candidate = Path(filepath)
        if candidate.is_absolute() and candidate.exists():
            continue
        roots = [root for root in (project_root, analysis_dir) if root]
        if not any((root / filepath).exists() for root in roots):
            issues.append({"level": "ERROR", "section": section,
                           "message": f"'{item_id}' grounded_in references non-existent file: {filepath}"})
    return issues


def check_existing_paths(
    paths: list,
    project_root: Path | None,
    analysis_dir: Path | None,
    section: str,
    item_id: str,
    *,
    label: str = "path",
) -> list[dict]:
    issues = []
    for raw_path in paths:
        if not raw_path:
            continue
        filepath = str(raw_path)
        candidate = Path(filepath)
        if candidate.is_absolute() and candidate.exists():
            continue
        roots = [root for root in (project_root, analysis_dir) if root]
        if not any((root / filepath).exists() for root in roots):
            issues.append({
                "level": "ERROR",
                "section": section,
                "message": f"'{item_id}' {label} references non-existent path: {filepath}",
            })
    return issues


def resolve_reference_file(
    ref: str,
    project_root: Path | None,
    analysis_dir: Path | None,
) -> Path | None:
    filepath = ref.split(":")[0]
    candidate = Path(filepath)
    if candidate.is_absolute():
        return candidate if candidate.exists() else None
    for root in (project_root, analysis_dir):
        if not root:
            continue
        resolved = root / filepath
        if resolved.exists():
            return resolved
    return None


def parse_reference_line(ref: str) -> int | None:
    parts = ref.rsplit(":", 1)
    if len(parts) != 2:
        return None
    try:
        return int(parts[1])
    except (TypeError, ValueError):
        return None


def tokenize_for_overlap(text: str) -> set[str]:
    return {
        token for token in re.findall(r"[A-Za-z0-9_./-]{3,}", text.lower())
        if not token.isdigit()
    }


def tokenize_identifiers(text: str) -> set[str]:
    identifiers: set[str] = set()
    for raw in re.findall(r"[A-Za-z_][A-Za-z0-9_./-]{2,}", text or ""):
        token = raw.strip().lower()
        if token.isdigit():
            continue
        if (
            "_" in raw
            or "/" in raw
            or "." in raw
            or "-" in raw
            or re.search(r"[A-Z]", raw)
            or re.search(r"[0-9]", raw)
        ):
            identifiers.add(token)
    return identifiers


def split_code_like_parts(text: str) -> set[str]:
    parts: set[str] = set()
    for raw in re.findall(r"[A-Za-z_][A-Za-z0-9_./-]{2,}", text or ""):
        normalized = raw.replace("/", " ").replace(".", " ").replace("-", " ").replace("_", " ")
        normalized = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", normalized)
        for part in normalized.split():
            token = part.lower()
            if len(token) >= 3 and not token.isdigit():
                parts.add(token)
    return parts


def tokenize_path_segments(path_text: str) -> set[str]:
    segments: set[str] = set()
    raw_path = path_text.split(":", 1)[0]
    for part in Path(raw_path).parts:
        lowered = part.lower()
        if lowered in {"", ".", ".."}:
            continue
        stem = Path(lowered).stem
        for token in split_code_like_parts(stem):
            segments.add(token)
        if len(lowered) >= 3 and lowered not in {stem, stem + Path(lowered).suffix}:
            segments.add(lowered)
    return segments


def verify_grounding_quality(
    refs: Iterable[str],
    claim_text: str,
    project_root: Path | None,
    analysis_dir: Path | None,
    section: str,
    item_id: str,
    evidence_snippet: str | None = None,
) -> list[dict]:
    issues = []
    claim_tokens = tokenize_for_overlap(claim_text or "")
    claim_identifiers = tokenize_identifiers(claim_text or "")
    claim_parts = split_code_like_parts(claim_text or "")
    evidence_tokens = tokenize_for_overlap(evidence_snippet or "")
    evidence_identifiers = tokenize_identifiers(evidence_snippet or "")
    evidence_parts = split_code_like_parts(evidence_snippet or "")
    if not claim_tokens:
        return issues
    for ref in refs:
        resolved = resolve_reference_file(ref, project_root, analysis_dir)
        if not resolved:
            continue
        line_no = parse_reference_line(ref)
        if line_no is None:
            issues.append({"level": "WARNING", "section": section, "message": f"'{item_id}' grounding reference has no valid line number: {ref}"})
            continue
        try:
            lines = resolved.read_text(encoding="utf-8", errors="ignore").splitlines()
        except OSError:
            continue
        if line_no < 1 or line_no > len(lines):
            issues.append({"level": "ERROR", "section": section, "message": f"'{item_id}' grounding line out of range for {resolved}: {line_no}"})
            continue
        start = max(0, line_no - 8)
        end = min(len(lines), line_no + 7)
        nearby_text = "\n".join(lines[start:end])
        nearby_tokens = tokenize_for_overlap(nearby_text)
        nearby_identifiers = tokenize_identifiers(nearby_text)
        nearby_parts = split_code_like_parts(nearby_text)
        path_overlap = claim_parts & tokenize_path_segments(ref)
        token_overlap = claim_tokens & (nearby_tokens | evidence_tokens)
        identifier_overlap = claim_identifiers & (nearby_identifiers | evidence_identifiers)
        part_overlap = claim_parts & (nearby_parts | evidence_parts)
        if not token_overlap and not identifier_overlap and not part_overlap and not path_overlap:
            issues.append({"level": "WARNING", "section": section, "message": f"'{item_id}' grounding at {ref} has weak code-shaped overlap with the claim"})
    return issues


def validate_evidence_file(
    filepath: str | None,
    lines: list | None,
    claim_text: str,
    project_root: Path | None,
    analysis_dir: Path | None,
    section: str,
    item_id: str,
) -> list[dict]:
    issues = []
    if not filepath:
        return issues
    resolved = resolve_reference_file(filepath, project_root, analysis_dir)
    if not resolved:
        issues.append({"level": "ERROR", "section": section, "message": f"'{item_id}' evidence references non-existent file: {filepath}"})
        return issues
    if not lines:
        issues.append({"level": "WARNING", "section": section, "message": f"'{item_id}' evidence is missing line numbers"})
        return issues
    try:
        content = resolved.read_text(encoding="utf-8", errors="ignore").splitlines()
    except OSError:
        return issues
    valid_refs: list[str] = []
    for raw_line in lines:
        if not isinstance(raw_line, int):
            issues.append({"level": "ERROR", "section": section, "message": f"'{item_id}' evidence line is not an integer: {raw_line}"})
            continue
        if raw_line < 1 or raw_line > len(content):
            issues.append({"level": "ERROR", "section": section, "message": f"'{item_id}' evidence line out of range for {filepath}: {raw_line}"})
            continue
        valid_refs.append(f"{filepath}:{raw_line}")
    snippet_text = "\n".join(content[line - 1] for line in lines if isinstance(line, int) and 1 <= line <= len(content))
    issues.extend(verify_grounding_quality(valid_refs, claim_text, project_root, analysis_dir, section, item_id, evidence_snippet=snippet_text))
    return issues


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
                "conflict_type": "fact_vs_semantic",
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
            "conflict_type": "fact_vs_semantic",
            "related_entities": [item_id, *[str(candidate.get('id') or '') for candidate in candidate_failure_scenarios[:2]]],
            "evidence_refs": [str(ref) for candidate in candidate_failure_scenarios for ref in (candidate.get("evidence_refs") or [])[:1]][:3],
        })
    return issues


def validate_atlas(
    atlas: dict,
    project_root: Path | None = None,
    analysis_dir: Path | None = None,
    concept_evidence_payload: dict | None = None,
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

    failure_scenario_candidates_payload = {}
    failure_scenario_candidates_path = analysis_dir / "facts" / "failure-scenario-candidates.json"
    if failure_scenario_candidates_path.exists():
        try:
            failure_scenario_candidates_payload = json.loads(failure_scenario_candidates_path.read_text())
        except json.JSONDecodeError as e:
            issues.append({"level": "ERROR", "section": "failure-scenario-candidates", "message": f"JSON parse error: {e}"})
    if isinstance(failure_scenario_candidates_payload, dict):
        for candidate in failure_scenario_candidates_payload.get("candidates") or []:
            if not isinstance(candidate, dict):
                continue
            for entity in [str(item) for item in (candidate.get("starts_at") or []) + (candidate.get("involves") or []) if str(item or "").strip()]:
                failure_scenario_candidates_by_entity[entity].append(candidate)

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
                "conflict_type": "fact_vs_semantic",
            })
        if candidate_health_gaps and not gap_affect_ids.get(cid):
            issues.append({
                "level": "WARNING",
                "section": "gaps",
                "kind": "gaps-model",
                "message": f"Component '{cid}' has deterministic health or resilience gaps but no top-level gap entry affects it",
                "related_entities": [cid],
                "evidence_refs": [str(ref) for candidate in candidate_health_gaps for ref in (candidate.get("evidence_refs") or [])[:1]][:3],
                "conflict_type": "fact_vs_semantic",
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
        if not f.get("grounded_in"):
            warn(f"Flow '{fid}' has no grounded_in", "flows")
        elif project_root or analysis_dir:
            issues.extend(check_grounded_in(f["grounded_in"], project_root, analysis_dir, "flows", fid))
            issues.extend(verify_grounding_quality(
                f["grounded_in"],
                " ".join(str(part) for part in (f.get("name"), f.get("title"), f.get("summary"), f.get("trigger")) if part),
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
            "message": "Deterministic route/job/event facts suggest the repo has meaningful actors, but atlas.actors is missing",
            "conflict_type": "fact_vs_semantic",
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
            "message": "Deterministic event facts suggest the repo has meaningful event boundaries, but atlas.events is missing",
            "conflict_type": "fact_vs_semantic",
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
            "message": "Deterministic model facts suggest the repo has a meaningful domain model, but atlas.domain_model is missing",
            "conflict_type": "fact_vs_semantic",
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
    if isinstance(concept_evidence_payload, dict):
        for fact in concept_evidence_payload.get("facts") or []:
            if not isinstance(fact, dict) or fact.get("kind") != "concept-candidate":
                continue
            raw = fact.get("raw_evidence") or {}
            concept_id = str(raw.get("concept_id") or "").strip()
            if not concept_id:
                continue
            if not raw.get("semantic_review_required"):
                continue
            concept_review_requirements[concept_id] = {
                "question_ids": list(((raw.get("semantic_questions") or {}).get("entry_ids") or [])),
                "detector_backing": str(raw.get("detector_backing") or ""),
            }

    # Concepts
    concepts = atlas.get("concepts", {})

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
        evidence = entry.get("evidence") or {}
        files = evidence.get("files") or []
        questions_asked = [str(item) for item in evidence.get("questions_asked") or [] if item]
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
                    f"{entry_kind.title()} '{cid}' was marked for semantic review by deterministic evidence but records no answered semantic questions",
                    "concepts",
                )
            elif review_requirement.get("question_ids"):
                missing = sorted(set(str(item) for item in review_requirement["question_ids"]) - set(questions_asked))
                if missing:
                    warn(
                        f"{entry_kind.title()} '{cid}' does not record all expected semantic questions from deterministic review: {', '.join(missing)}",
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
            "evidence_refs": ["facts/index.json", "facts/frameworks.json"],
            "conflict_type": "fact_vs_semantic",
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
                "evidence_refs": ["facts/index.json", "facts/frameworks.json"],
                "conflict_type": "fact_vs_semantic",
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
                "evidence_refs": ["facts/index.json", "facts/frameworks.json"],
                "conflict_type": "fact_vs_semantic",
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
                "evidence_refs": ["facts/index.json", "facts/frameworks.json"],
                "conflict_type": "fact_vs_semantic",
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
                    "conflict_type": "fact_vs_semantic",
                })
            if framework_facts and name not in framework_facts:
                issues.append({
                    "level": "WARNING",
                    "section": "metadata",
                    "kind": "framework-resolution",
                    "message": f"metadata.frameworks includes '{name}' but deterministic framework facts do not support it in this run",
                    "related_entities": [name],
                    "evidence_refs": [],
                    "conflict_type": "fact_vs_semantic",
                })

        for name, fact in framework_facts.items():
            confidence = str(fact.get("confidence") or "").lower()
            if confidence not in {"medium", "high"}:
                continue
            if name not in framework_names_in_meta:
                issues.append({
                    "level": "WARNING",
                    "section": "metadata",
                    "kind": "framework-resolution",
                    "message": f"Deterministic framework evidence suggests '{name}' but metadata.frameworks does not record a resolved entry",
                    "related_entities": [name],
                    "evidence_refs": list(fact.get("source_files") or [])[:3],
                    "conflict_type": "fact_vs_semantic",
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
                "conflict_type": "fact_vs_semantic",
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

    if isinstance(failure_scenario_candidates_payload, dict):
        present_ids = seen_failure_scenario_ids
        for candidate in failure_scenario_candidates_payload.get("candidates") or []:
            if not isinstance(candidate, dict):
                continue
            candidate_id = str(candidate.get("id") or "")
            if not candidate_id or candidate_id in present_ids:
                continue
            involves = [str(item) for item in (candidate.get("involves") or []) if str(item or "").strip()]
            if len(involves) < 2:
                continue
            issues.append({
                "level": "WARNING",
                "section": "failure_scenarios",
                "kind": "failure-scenario-missing",
                "message": f"Shared failure candidate '{candidate_id}' is not modeled in atlas.failure_scenarios",
                "conflict_type": "fact_vs_semantic",
                "related_entities": [candidate_id, *involves[:3]],
                "evidence_refs": [str(ref) for ref in (candidate.get("evidence_refs") or [])[:3]],
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


def validate_story(
    story: dict,
    atlas_node_ids: set,
    atlas_entity_ids: set,
    atlas_story_node_details: dict[str, dict] | None = None,
    project_root: Path | None = None,
    analysis_dir: Path | None = None,
) -> list[dict]:
    issues = []
    atlas_story_node_details = atlas_story_node_details or {}
    warned_story_node_detail_ids: set[str] = set()
    allowed_primary_modes = {"structure", "flow", "state", "failure", "decision"}

    def error(msg):
        issues.append({"level": "ERROR", "section": "story", "message": msg})

    def warn(msg):
        issues.append({"level": "WARNING", "section": "story", "message": msg})

    def warn_story_node_detail(nid: str):
        if nid in warned_story_node_detail_ids:
            return
        warned_story_node_detail_ids.add(nid)
        detail = atlas_story_node_details.get(nid) or {}
        if not detail:
            return
        description = str(detail.get("description") or "").strip()
        summary = str(detail.get("summary") or "").strip()
        kind = str(detail.get("kind") or "atlas node")
        if not description:
            issues.append({
                "level": "WARNING",
                "section": "story",
                "kind": "story-quality",
                "message": f"Story '{sid}' uses {kind} '{nid}' but it has no description; story-used atlas nodes need basic drilldown prose",
                "related_entities": [sid, nid],
            })
        if not summary:
            issues.append({
                "level": "WARNING",
                "section": "story",
                "kind": "story-quality",
                "message": f"Story '{sid}' uses {kind} '{nid}' but it has no summary; story-used atlas nodes need richer drilldown prose for the drawer",
                "related_entities": [sid, nid],
            })
        elif len(summary.split()) < 12:
            issues.append({
                "level": "WARNING",
                "section": "story",
                "kind": "story-quality",
                "message": f"Story '{sid}' uses {kind} '{nid}' but its summary is too thin for drilldown; explain ownership, dependency shape, and why it matters",
                "related_entities": [sid, nid],
            })

    sid = story.get("id", "<unknown>")
    parent_story = story.get("parent")

    if "id" not in story:
        error(f"Story missing required field: id")
    if "title" not in story:
        error(f"Story '{sid}' missing required field: title")
    if "teaches" not in story:
        error(f"Story '{sid}' missing required field: teaches")
    if "primary_mode" not in story:
        error(f"Story '{sid}' missing required field: primary_mode")
    if "summary" not in story:
        error(f"Story '{sid}' missing required field: summary")

    primary_mode = str(story.get("primary_mode") or "").strip()
    if primary_mode and primary_mode not in allowed_primary_modes:
        error(
            f"Story '{sid}' primary_mode '{primary_mode}' is invalid; use one of: "
            + ", ".join(sorted(allowed_primary_modes))
        )

    teaches_text = str(story.get("teaches") or "").strip()
    if teaches_text:
        if len(teaches_text.split()) < 5:
            warn(f"Story '{sid}' teaches is too thin; make it a real thesis sentence")
        if len(re.findall(r"[.!?]", teaches_text)) > 1:
            warn(f"Story '{sid}' teaches should usually stay to one sentence")
    else:
        warn(f"Story '{sid}' teaches is empty; make the main lesson explicit")

    anchor = story.get("anchor")
    if not isinstance(anchor, dict):
        error(f"Story '{sid}' missing required object field: anchor")
    else:
        anchor_file = anchor.get("file")
        anchor_line = anchor.get("line")
        anchor_description = anchor.get("description")
        if not anchor_file:
            error(f"Story '{sid}' anchor is missing file")
        elif project_root or analysis_dir:
            issues.extend(check_grounded_in([f"{anchor_file}:{anchor_line or 1}"], project_root, analysis_dir, "story", f"{sid}/anchor"))
            issues.extend(verify_grounding_quality(
                [f"{anchor_file}:{anchor_line or 1}"],
                " ".join(str(part) for part in (anchor_description, story.get("title"), story.get("summary")) if part),
                project_root,
                analysis_dir,
                "story",
                f"{sid}/anchor",
            ))
        if not isinstance(anchor_line, int):
            error(f"Story '{sid}' anchor line must be an integer")
        if not anchor_description:
            error(f"Story '{sid}' anchor is missing description")

    # Summary word count
    summary = story.get("summary", "")
    word_count = len(summary.split())
    if word_count > 100:
        warn(f"Story '{sid}' summary is {word_count} words (max 100)")
    if word_count < 18:
        warn(f"Story '{sid}' summary is thin; use it to explain the concern, not just relabel it")

    structures = story.get("structures", []) or []
    flows = story.get("flows", []) or []
    observations = story.get("observations", []) or []
    rationale_entries = story.get("rationale", []) or []
    if not (structures or flows or observations or rationale_entries):
        error(f"Story '{sid}' has no primary explainer or support content")

    # Bold refs in summary should resolve to atlas entities, not filenames or fact artifacts.
    bold_refs = re.findall(r"\*\*([^*]+)\*\*", summary)
    for ref in bold_refs:
        ref_kebab = ref.lower().replace(" ", "-")
        if ref_kebab not in atlas_entity_ids and ref not in atlas_entity_ids:
            error(f"Story '{sid}' bold ref '**{ref}**' doesn't match any atlas entity")

    # Structure node refs
    for struct in structures:
        structure_edges = struct.get("edges", []) or []
        referenced_by_edge = set()
        for edge in structure_edges:
            if isinstance(edge, dict):
                if edge.get("from"):
                    referenced_by_edge.add(edge.get("from"))
                if edge.get("to"):
                    referenced_by_edge.add(edge.get("to"))
        for node in struct.get("nodes", []):
            nid = node.get("id", "") if isinstance(node, dict) else node
            if nid and nid not in atlas_node_ids:
                error(f"Story '{sid}' structure node '{nid}' not in atlas")
            elif nid:
                warn_story_node_detail(nid)
            if isinstance(node, dict):
                observation_ids = [obs_id for obs_id in (node.get("observation_ids") or []) if obs_id]
                child_ids = [child_id for child_id in (node.get("children") or []) if child_id]
                if child_ids and not observation_ids:
                    issues.append({
                        "level": "WARNING",
                        "section": "story",
                        "kind": "story-quality",
                        "message": f"Story '{sid}' structure node '{nid}' groups children but has no observation_ids grounding that grouping",
                        "related_entities": [sid, nid, *child_ids[:2]],
                    })
                if not child_ids and not observation_ids and nid not in referenced_by_edge:
                    issues.append({
                        "level": "WARNING",
                        "section": "story",
                        "kind": "story-quality",
                        "message": f"Story '{sid}' structure node '{nid}' is weakly grounded; add observation_ids or connect it through explicit structure edges",
                        "related_entities": [sid, nid],
                    })
        for edge in struct.get("edges", []):
            for key in ("from", "to"):
                ref = edge.get(key, "")
                if ref and ref not in atlas_node_ids:
                    error(f"Story '{sid}' structure edge {key} '{ref}' not in atlas")

    # Flow node refs
    flow_titles_or_summaries: list[str] = []
    for flow in flows:
        flow_summary = str(flow.get("summary") or "").strip()
        flow_title = str(flow.get("title") or "").strip()
        if flow_title:
            flow_titles_or_summaries.append(flow_title)
        if flow_summary:
            flow_titles_or_summaries.append(flow_summary)
        if primary_mode == "flow":
            if not flow_summary:
                issues.append({
                    "level": "WARNING",
                    "section": "story",
                    "kind": "story-quality",
                    "message": f"Flow-first story '{sid}' should give each primary flow a short summary explaining why it matters",
                    "related_entities": [sid, str(flow.get("id") or "?")],
                })
            elif len(flow_summary.split()) < 6:
                issues.append({
                    "level": "WARNING",
                    "section": "story",
                    "kind": "story-quality",
                    "message": f"Flow-first story '{sid}' flow '{flow.get('id', '?')}' has a thin summary; explain trigger, outcome, or architectural significance",
                    "related_entities": [sid, str(flow.get("id") or "?")],
                })
        if "path" in flow_title.lower() or "path" in flow_summary.lower():
            issues.append({
                "level": "WARNING",
                "section": "story",
                "kind": "story-quality",
                "message": f"Story '{sid}' flow '{flow.get('id', '?')}' uses 'path' wording; prefer 'flow' consistently in the story contract",
                "related_entities": [sid, str(flow.get("id") or "?")],
            })
        for step in flow.get("steps", []):
            for key in ("node", "to"):
                ref = step.get(key, "")
                if ref and ref not in atlas_node_ids:
                    error(f"Story '{sid}' flow step {key} '{ref}' not in atlas")
                elif ref:
                    warn_story_node_detail(ref)

    # Observation grounded_in
    for obs in observations:
        oid = obs.get("id", "?")
        finding = obs.get("finding", "")
        if not obs.get("grounded_in"):
            warn(f"Story '{sid}' observation '{oid}' has no grounded_in")
        elif project_root or analysis_dir:
            issues.extend(check_grounded_in(obs["grounded_in"], project_root, analysis_dir, "story", f"{sid}/{oid}"))
            issues.extend(verify_grounding_quality(obs["grounded_in"], finding, project_root, analysis_dir, "story", f"{sid}/{oid}"))
        evidence = obs.get("evidence") if isinstance(obs.get("evidence"), dict) else None
        if evidence and (project_root or analysis_dir):
            issues.extend(validate_evidence_file(
                evidence.get("file"),
                evidence.get("lines"),
                finding,
                project_root,
                analysis_dir,
                "story",
                f"{sid}/{oid}/evidence",
            ))
        comp = obs.get("component", "")
        if comp and comp not in atlas_node_ids:
            error(f"Story '{sid}' observation component '{comp}' not in atlas")

    if len(observations) > 4:
        issues.append({
            "level": "WARNING",
            "section": "story",
            "kind": "story-quality",
            "message": f"Story '{sid}' has many observations ({len(observations)}); keep the visible story focused and push extra evidence into support material only when it changes understanding",
            "related_entities": [sid],
        })
    if len(rationale_entries) > 3:
        issues.append({
            "level": "WARNING",
            "section": "story",
            "kind": "story-quality",
            "message": f"Story '{sid}' has many rationale entries ({len(rationale_entries)}); keep decisions selective unless the story is decision-first",
            "related_entities": [sid],
        })

    thesis_text = " ".join(part for part in (teaches_text, str(story.get("title") or ""), summary) if part).lower()
    state_tokens = ("state", "storage", "persist", "cache", "queue", "snapshot", "config", "session")
    failure_tokens = ("fail", "degrad", "stale", "lag", "retry", "outage", "incident", "recovery", "mitigat", "cascade")
    decision_tokens = ("trade-off", "tradeoff", "decision", "choose", "constraint", "because", "alternative")
    has_failure_support = any(token in thesis_text for token in failure_tokens) or any(
        any(
            token in " ".join(
                str(part) for part in (entry.get("decision"), entry.get("context"), entry.get("trade_offs")) if part
            ).lower()
            for token in failure_tokens
        )
        for entry in rationale_entries if isinstance(entry, dict)
    ) or any(
        any(
            token in " ".join(str(part) for part in (obs.get("finding"), obs.get("recommendation")) if part).lower()
            for token in failure_tokens
        )
        for obs in observations if isinstance(obs, dict)
    )

    if primary_mode == "structure":
        if not structures:
            error(f"Structure-first story '{sid}' is missing structures")
        if len(structures) > 2:
            warn(f"Structure-first story '{sid}' has too many structure views; keep one primary explainer and at most one supporting variant")
        if flows and len(flows) > len(structures):
            warn(f"Structure-first story '{sid}' includes more flows than structures; keep the structural explainer dominant")
    elif primary_mode == "flow":
        if not flows:
            error(f"Flow-first story '{sid}' is missing flows")
        if len(flows) > 2:
            warn(f"Flow-first story '{sid}' has too many flows; keep one primary flow and at most one supporting flow")
        if structures and len(structures) > len(flows):
            warn(f"Flow-first story '{sid}' includes more structure views than flows; keep the flow explainer dominant")
    elif primary_mode == "state":
        if not (structures or flows):
            error(f"State-first story '{sid}' should include a structure or flow that explains the state boundary")
        if not any(token in thesis_text for token in state_tokens):
            warn(f"State-first story '{sid}' thesis and summary do not clearly read as state-focused")
    elif primary_mode == "failure":
        if not (flows or observations):
            error(f"Failure-first story '{sid}' should include a flow or observation set that explains the failure mode")
        if not has_failure_support:
            warn(f"Failure-first story '{sid}' does not clearly describe degraded behavior, failure, or recovery")
    elif primary_mode == "decision":
        if not rationale_entries:
            error(f"Decision-first story '{sid}' is missing rationale")
        if not any(token in thesis_text for token in decision_tokens):
            warn(f"Decision-first story '{sid}' thesis and summary do not clearly frame the design choice or trade-off")
        if structures and flows and len(rationale_entries) < 1:
            warn(f"Decision-first story '{sid}' is leaning on structure and flow explainers without enough explicit rationale")

    if parent_story:
        child_nodes: set[str] = set()
        for struct in structures:
            for node in struct.get("nodes", []):
                if isinstance(node, dict):
                    nid = str(node.get("id") or "")
                else:
                    nid = str(node or "")
                if nid:
                    child_nodes.add(nid)
        if len(child_nodes) >= max(4, len(atlas_node_ids) // 3):
            warn(f"Story '{sid}' may be too broad for a child story; narrow the node set relative to its parent")

    return issues


def validate_narrative(narrative: dict, story_ids: set) -> list[dict]:
    issues = []

    def error(msg):
        issues.append({"level": "ERROR", "section": "narrative", "message": msg})

    def warn(msg):
        issues.append({"level": "WARNING", "section": "narrative", "message": msg})

    jid = narrative.get("id", "<unknown>")

    if "id" not in narrative:
        error("Narrative missing required field: id")
    if "title" not in narrative:
        error(f"Narrative '{jid}' missing required field: title")
    if "description" not in narrative:
        error(f"Narrative '{jid}' missing required field: description")
    if jid and jid not in CANONICAL_NARRATIVE_IDS:
        error(
            f"Narrative '{jid}' is outside the canonical narrative palette; use one of: "
            + ", ".join(sorted(CANONICAL_NARRATIVE_IDS))
        )

    stories = narrative.get("stories", [])
    teaches = narrative.get("teaches")
    throughline = str(narrative.get("throughline") or "").strip()
    description = str(narrative.get("description") or "").strip()
    sentence_count = len([part for part in re.split(r"(?<=[.!?])\s+", description) if part.strip()]) if description else 0
    if len(stories) < 3:
        warn(f"Narrative '{jid}' has {len(stories)} stories (minimum 3)")
    elif len(stories) > 8:
        warn(f"Narrative '{jid}' has {len(stories)} stories (maximum 8)")
    if description:
        if sentence_count < 2:
            issues.append({
                "level": "WARNING",
                "section": "narrative",
                "kind": "narrative-overview",
                "message": f"Narrative '{jid}' description is too thin; write a compact 2-4 sentence overview instead of a one-liner",
            })
        elif sentence_count > 5:
            issues.append({
                "level": "WARNING",
                "section": "narrative",
                "kind": "narrative-overview",
                "message": f"Narrative '{jid}' description is too long for the overview slot; keep it to roughly 2-4 sentences",
            })
    if teaches is None:
        issues.append({
            "level": "WARNING",
            "section": "narrative",
            "kind": "narrative-coherence",
            "message": f"Narrative '{jid}' is missing `teaches`; define 2-4 explicit learning goals for the sequence",
        })
    elif not isinstance(teaches, list):
        error(f"Narrative '{jid}' teaches must be a list when present")
    else:
        cleaned_goals = [goal for goal in teaches if isinstance(goal, str) and goal.strip()]
        if len(cleaned_goals) < 2:
            issues.append({
                "level": "WARNING",
                "section": "narrative",
                "kind": "narrative-coherence",
                "message": f"Narrative '{jid}' should define at least 2 teaching goals in `teaches`",
            })
        elif len(cleaned_goals) > 4:
            issues.append({
                "level": "WARNING",
                "section": "narrative",
                "kind": "narrative-coherence",
                "message": f"Narrative '{jid}' has too many teaching goals; keep `teaches` to roughly 2-4 items",
            })
    if not throughline:
        issues.append({
            "level": "WARNING",
            "section": "narrative",
            "kind": "narrative-coherence",
            "message": f"Narrative '{jid}' is missing `throughline`; explain why these stories belong together in this order",
        })
    else:
        throughline_sentences = len([part for part in re.split(r"(?<=[.!?])\s+", throughline) if part.strip()])
        if throughline_sentences > 3:
            issues.append({
                "level": "WARNING",
                "section": "narrative",
                "kind": "narrative-coherence",
                "message": f"Narrative '{jid}' throughline is too long; keep it to one short paragraph",
            })

    for entry in stories:
        if isinstance(entry, dict):
            sid = entry.get("id", "")
            if not entry.get("description"):
                error(f"Narrative '{jid}' story '{sid or '?'}' is missing description")
        else:
            sid = entry
        if sid not in story_ids:
            error(f"Narrative '{jid}' references unknown story '{sid}'")

    return issues


def detect_cross_artifact_conflicts(
    atlas: dict,
    all_stories: dict[str, dict],
    narratives: list[dict],
    narrative_seeds_payload: dict | None = None,
    control_hotspots_payload: dict | None = None,
    state_access_summary_payload: dict | None = None,
) -> list[dict]:
    issues: list[dict] = []
    components = {
        str(component.get("id")): component
        for component in (atlas.get("components") or [])
        if isinstance(component, dict) and component.get("id")
    }
    state_ids = {
        str(state.get("id"))
        for state in (atlas.get("state") or [])
        if isinstance(state, dict) and state.get("id")
    }
    depends_on = {
        cid: set(str(dep) for dep in (component.get("depends_on") or []) if dep)
        for cid, component in components.items()
    }
    child_story_ids_by_parent: dict[str, list[str]] = {}
    for sid, story in all_stories.items():
        parent = str(story.get("parent") or "")
        if parent:
            child_story_ids_by_parent.setdefault(parent, []).append(sid)

    def story_root(story_id: str) -> str:
        current = all_stories.get(story_id) or {}
        seen: set[str] = set()
        current_id = story_id
        while current.get("parent") and current_id not in seen:
            seen.add(current_id)
            current_id = str(current.get("parent") or "")
            current = all_stories.get(current_id) or {}
        return current_id or story_id

    def story_component_ids(story: dict) -> set[str]:
        ids: set[str] = set()
        for struct in story.get("structures") or []:
            for node in struct.get("nodes") or []:
                nid = str(node.get("id") or "") if isinstance(node, dict) else str(node or "")
                if nid in components:
                    ids.add(nid)
        for flow in story.get("flows") or []:
            for step in flow.get("steps") or []:
                if not isinstance(step, dict):
                    continue
                component = str(step.get("node") or step.get("component") or "")
                target = str(step.get("to") or "")
                if component in components:
                    ids.add(component)
                if target in components:
                    ids.add(target)
        for obs in story.get("observations") or []:
            if isinstance(obs, dict):
                component = str(obs.get("component") or "")
                if component in components:
                    ids.add(component)
        return ids

    root_to_story_ids: dict[str, list[str]] = {}
    for sid in all_stories:
        root_to_story_ids.setdefault(story_root(sid), []).append(sid)

    control_hotspots_by_component: dict[str, list[dict]] = {}
    if isinstance(control_hotspots_payload, dict):
        for fact in control_hotspots_payload.get("facts") or []:
            if not isinstance(fact, dict):
                continue
            raw = fact.get("raw_evidence") or {}
            component = str(raw.get("component") or "")
            if component:
                control_hotspots_by_component.setdefault(component, []).append(fact)

    state_access_by_component: dict[str, list[dict]] = {}
    if isinstance(state_access_summary_payload, dict):
        for fact in state_access_summary_payload.get("facts") or []:
            if not isinstance(fact, dict):
                continue
            raw = fact.get("raw_evidence") or {}
            for component in raw.get("components") or []:
                component = str(component or "")
                if component:
                    state_access_by_component.setdefault(component, []).append(fact)

    system_overview_seed = (
        (narrative_seeds_payload or {}).get("system_overview") or {}
        if isinstance(narrative_seeds_payload, dict)
        else {}
    )
    recommended_narrative_records = [
        item
        for item in ((narrative_seeds_payload or {}).get("recommended_narratives") or [])
        if isinstance(item, dict) and str(item.get("id") or "")
    ] if isinstance(narrative_seeds_payload, dict) else []
    recommended_narrative_ids = {
        str(item.get("id") or "")
        for item in recommended_narrative_records
    }
    recommended_narrative_by_id = {
        str(item.get("id") or ""): item
        for item in recommended_narrative_records
    }
    optional_recommended_ids = {
        narrative_id
        for narrative_id in recommended_narrative_ids
        if narrative_id and narrative_id != "system-overview"
    }
    optional_recommended_records = [
        item
        for item in recommended_narrative_records
        if str(item.get("id") or "") in optional_recommended_ids
    ]
    optional_recommended_records.sort(
        key=lambda item: (
            -int(item.get("score") or 0),
            int(item.get("priority_rank") or 999),
            str(item.get("id") or ""),
        )
    )
    optional_budget = (
        (narrative_seeds_payload or {}).get("optional_narrative_budget") or {}
        if isinstance(narrative_seeds_payload, dict)
        else {}
    )
    preferred_optional_target = int(optional_budget.get("target") or 0)
    preferred_roots = [
        item for item in (system_overview_seed.get("preferred_root_components") or [])
        if isinstance(item, dict)
    ]
    preferred_flow_hotspots = [
        item for item in (system_overview_seed.get("preferred_flow_hotspots") or [])
        if isinstance(item, dict)
    ]
    preferred_boundary_targets = [
        item for item in (system_overview_seed.get("preferred_state_or_boundary_targets") or [])
        if isinstance(item, dict)
    ]
    preferred_root_ids = [str(item.get("id") or "") for item in preferred_roots if item.get("id")]
    require_flow_story = bool(system_overview_seed.get("require_flow_story"))
    require_state_or_boundary_story = bool(system_overview_seed.get("require_state_or_boundary_story"))
    prefer_child_stories = bool(system_overview_seed.get("prefer_child_stories"))
    present_ids = {
        str(narrative.get("id") or "")
        for narrative in narratives
        if isinstance(narrative, dict)
    }

    def text_tokens(value: str) -> set[str]:
        return {
            token
            for token in re.findall(r"[a-z0-9]+", value.lower())
            if len(token) > 3 and token not in {"this", "that", "with", "from", "into", "through", "their", "about", "because", "where", "which", "story", "next", "then"}
        }

    for sid, story in all_stories.items():
        for structure in story.get("structures") or []:
            for edge in structure.get("edges") or []:
                if not isinstance(edge, dict):
                    continue
                edge_type = str(edge.get("type") or "").lower()
                if edge_type not in {"calls", "reads", "writes"}:
                    continue
                source = str(edge.get("from") or "")
                target = str(edge.get("to") or "")
                if source not in components or target not in components or source == target:
                    continue
                if target in depends_on.get(source, set()):
                    continue
                if source in depends_on.get(target, set()):
                    issues.append(
                        {
                            "level": "WARNING",
                            "section": "components",
                            "kind": "component-model",
                            "message": (
                                f"Story '{sid}' implies '{source}' -> '{target}' via a '{edge_type}' edge, "
                                f"but atlas depends_on points the opposite direction"
                            ),
                            "conflict_type": "cross_artifact",
                            "related_entities": [sid, source, target],
                            "evidence_refs": [],
                        }
                    )

    for narrative in narratives:
        if not isinstance(narrative, dict):
            continue
        nid = str(narrative.get("id") or "")
        description = str(narrative.get("description") or "").strip()
        teaches = narrative.get("teaches") if isinstance(narrative.get("teaches"), list) else []
        throughline = str(narrative.get("throughline") or "").strip()
        story_entries = narrative.get("stories") or []
        referenced_story_ids = []
        for entry in story_entries:
            if isinstance(entry, dict):
                story_id = str(entry.get("id") or "")
            else:
                story_id = str(entry or "")
            if story_id:
                referenced_story_ids.append(story_id)
        referenced_set = set(referenced_story_ids)
        recommended_record = recommended_narrative_by_id.get(nid)
        if nid != "system-overview" and nid in CANONICAL_NARRATIVE_IDS and recommended_record is None:
            issues.append(
                {
                    "level": "WARNING",
                    "section": "narrative",
                    "kind": "narrative-selection",
                    "message": f"Narrative '{nid}' is in the canonical palette but is not strongly justified by deterministic narrative seeds",
                    "conflict_type": "fact_vs_semantic",
                    "related_entities": [nid, *referenced_story_ids[:3]],
                    "evidence_refs": [],
                }
            )
        if nid != "system-overview" and nid in CANONICAL_NARRATIVE_IDS and recommended_record is not None:
            present_optional_ids = {
                story_nid
                for story_nid in present_ids
                if story_nid and story_nid != "system-overview"
            }
            stronger_missing = [
                item
                for item in optional_recommended_records
                if str(item.get("id") or "") not in present_optional_ids
                and int(item.get("score") or 0) >= int(recommended_record.get("score") or 0) + 10
            ]
            if stronger_missing:
                stronger = stronger_missing[0]
                issues.append(
                    {
                        "level": "WARNING",
                        "section": "narrative",
                        "kind": "narrative-selection",
                        "message": (
                            f"Narrative '{nid}' is weaker than the stronger deterministic optional narrative "
                            f"'{str(stronger.get('id') or '')}', which is missing from the repo's selected teaching paths"
                        ),
                        "conflict_type": "fact_vs_semantic",
                        "related_entities": [nid, str(stronger.get("id") or "")],
                        "evidence_refs": [],
                    }
                )
        missing_child_coverage: list[str] = []
        for story_id in referenced_story_ids:
            child_ids = child_story_ids_by_parent.get(story_id) or []
            if len(child_ids) < 2:
                continue
            if not any(child_id in referenced_set for child_id in child_ids):
                missing_child_coverage.append(story_id)
        if missing_child_coverage:
            issues.append(
                {
                    "level": "WARNING",
                    "section": "narrative",
                    "kind": "narrative-selection",
                    "message": (
                        f"Narrative '{nid}' uses root stories {', '.join(sorted(missing_child_coverage))} "
                        "without any of their more specific child stories"
                    ),
                    "conflict_type": "cross_artifact",
                    "related_entities": [nid, *sorted(missing_child_coverage)],
                    "evidence_refs": [],
                }
            )

        if teaches:
            story_teaching_text = [
                " ".join(
                    str(part)
                    for part in (
                        (all_stories.get(story_id) or {}).get("teaches"),
                        (all_stories.get(story_id) or {}).get("title"),
                        (all_stories.get(story_id) or {}).get("summary"),
                    )
                    if part
                )
                for story_id in referenced_story_ids
                if story_id in all_stories
            ]
            story_tokens = set().union(*(text_tokens(text) for text in story_teaching_text)) if story_teaching_text else set()
            uncovered_goals = []
            for goal in teaches:
                if not isinstance(goal, str) or not goal.strip():
                    continue
                goal_tokens = text_tokens(goal)
                if goal_tokens and len(goal_tokens & story_tokens) == 0:
                    uncovered_goals.append(goal)
            if uncovered_goals:
                issues.append(
                    {
                        "level": "WARNING",
                        "section": "narrative",
                        "kind": "narrative-coherence",
                        "message": f"Narrative '{nid}' includes teaching goals that are not clearly served by the selected stories: {', '.join(uncovered_goals[:2])}",
                        "conflict_type": "cross_artifact",
                        "related_entities": [nid, *referenced_story_ids],
                        "evidence_refs": [],
                    }
                )

        if throughline:
            throughline_tokens = text_tokens(throughline)
            story_focus_tokens = set()
            for story_id in referenced_story_ids:
                story = all_stories.get(story_id) or {}
                story_focus_tokens |= text_tokens(" ".join(str(part) for part in (story.get("teaches"), story.get("title")) if part))
            if throughline_tokens and story_focus_tokens and len(throughline_tokens & story_focus_tokens) == 0:
                issues.append(
                    {
                        "level": "WARNING",
                        "section": "narrative",
                        "kind": "narrative-coherence",
                        "message": f"Narrative '{nid}' throughline does not clearly connect to the selected stories",
                        "conflict_type": "cross_artifact",
                        "related_entities": [nid, *referenced_story_ids],
                        "evidence_refs": [],
                    }
                )

            story_without_goal_support = []
            goal_tokens = [text_tokens(goal) for goal in teaches if isinstance(goal, str) and goal.strip()]
            for story_id in referenced_story_ids:
                story = all_stories.get(story_id) or {}
                story_text = " ".join(
                    str(part)
                    for part in (story.get("teaches"), story.get("title"), story.get("summary"))
                    if part
                )
                story_tokens = text_tokens(story_text)
                if goal_tokens and story_tokens and not any(story_tokens & goal for goal in goal_tokens):
                    story_without_goal_support.append(story_id)
            if story_without_goal_support:
                issues.append(
                    {
                        "level": "WARNING",
                        "section": "narrative",
                        "kind": "narrative-coherence",
                        "message": f"Narrative '{nid}' includes stories that do not clearly support its teaching goals: {', '.join(story_without_goal_support[:2])}",
                        "conflict_type": "cross_artifact",
                        "related_entities": [nid, *story_without_goal_support],
                        "evidence_refs": [],
                    }
                )

        transition_failures = []
        for index, entry in enumerate(story_entries):
            if index == 0 or not isinstance(entry, dict):
                continue
            bridge_text = str(entry.get("description") or "").strip()
            current_story_id = str(entry.get("id") or "")
            previous_entry = story_entries[index - 1]
            previous_story_id = str(previous_entry.get("id") if isinstance(previous_entry, dict) else previous_entry or "")
            previous_story = all_stories.get(previous_story_id) or {}
            current_story = all_stories.get(current_story_id) or {}
            transition_tokens = text_tokens(bridge_text)
            previous_tokens = text_tokens(" ".join(str(part) for part in (previous_story.get("teaches"), previous_story.get("title")) if part))
            current_tokens = text_tokens(" ".join(str(part) for part in (current_story.get("teaches"), current_story.get("title")) if part))
            if bridge_text and transition_tokens and (transition_tokens & previous_tokens) and (transition_tokens & current_tokens):
                continue
            transition_failures.append(current_story_id or f"story-{index+1}")
        if transition_failures:
            issues.append(
                {
                    "level": "WARNING",
                    "section": "narrative",
                    "kind": "narrative-coherence",
                    "message": f"Narrative '{nid}' has weak adjacent-story transitions; bridge text does not clearly connect the sequence around: {', '.join(transition_failures[:2])}",
                    "conflict_type": "cross_artifact",
                    "related_entities": [nid, *transition_failures],
                    "evidence_refs": [],
                }
            )

        if nid == "system-overview" and description:
            top_level_components = [
                component
                for component in components.values()
                if not component.get("parent") and not component.get("belongs_to")
            ]
            sentence_count = len([part for part in re.split(r"(?<=[.!?])\s+", description) if part.strip()])
            if sentence_count < 3:
                issues.append(
                    {
                        "level": "WARNING",
                        "section": "narrative",
                        "kind": "narrative-overview",
                        "message": "system-overview description is too short to serve as the repo overview; use roughly 3-4 sentences",
                        "conflict_type": "cross_artifact",
                        "related_entities": [nid],
                        "evidence_refs": [],
                    }
                )
            lowered = description.lower()
            covered = 0
            for component in top_level_components:
                candidates = {
                    str(component.get("id") or "").lower(),
                    str(component.get("name") or "").lower(),
                }
                if any(candidate and candidate in lowered for candidate in candidates):
                    covered += 1
            expected_mentions = min(2, len(top_level_components))
            if expected_mentions and covered < expected_mentions:
                issues.append(
                    {
                        "level": "WARNING",
                        "section": "narrative",
                        "kind": "narrative-overview",
                        "message": "system-overview description does not name enough of the main top-level slices to function as a useful repo overview",
                        "conflict_type": "cross_artifact",
                        "related_entities": [nid, *[str(component.get('id')) for component in top_level_components]],
                        "evidence_refs": [],
                    }
                )
            teach_text = " ".join(
                [description, throughline]
                + [str(goal) for goal in teaches if isinstance(goal, str)]
            ).lower()
            what_tokens = {"purpose", "capability", "serves", "provides", "answers", "classifies", "stores", "scans", "emits", "manages", "handles"}
            how_tokens = {"flow", "pipeline", "path", "through", "runtime", "control", "orchestrates", "routes", "executes", "persists", "publishes"}
            if not any(token in teach_text for token in what_tokens):
                issues.append(
                    {
                        "level": "WARNING",
                        "section": "narrative",
                        "kind": "narrative-overview",
                        "message": "system-overview does not clearly answer what the system does; make the repo capability explicit in description or teaches",
                        "conflict_type": "cross_artifact",
                        "related_entities": [nid],
                        "evidence_refs": [],
                    }
                )
            if not any(token in teach_text for token in how_tokens):
                issues.append(
                    {
                        "level": "WARNING",
                        "section": "narrative",
                        "kind": "narrative-overview",
                        "message": "system-overview does not clearly answer how the system does it; make the operating model explicit in description, teaches, or throughline",
                        "conflict_type": "cross_artifact",
                        "related_entities": [nid],
                        "evidence_refs": [],
                    }
                )

        if nid == "system-overview":
            selected_roots = {story_root(story_id) for story_id in referenced_story_ids if story_id in all_stories}
            if preferred_root_ids:
                expected_root_count = min(2, len(preferred_root_ids))
                covered_preferred = [root_id for root_id in preferred_root_ids if root_id in selected_roots]
                if len(covered_preferred) < expected_root_count:
                    missing = [root_id for root_id in preferred_root_ids[:expected_root_count] if root_id not in covered_preferred]
                    evidence_refs = []
                    for item in preferred_roots[:expected_root_count]:
                        for ref in item.get("representative_files") or []:
                            ref = str(ref)
                            if ref and ref not in evidence_refs:
                                evidence_refs.append(ref)
                    issues.append(
                        {
                            "level": "WARNING",
                            "section": "narrative",
                            "kind": "narrative-selection",
                        "message": f"system-overview omits preferred repo-overview roots suggested by deterministic evidence: {', '.join(missing[:2])}",
                            "conflict_type": "fact_vs_semantic",
                            "related_entities": [nid, *missing],
                            "evidence_refs": evidence_refs[:3],
                        }
                    )

            selected_stories = [all_stories.get(story_id) or {} for story_id in referenced_story_ids if story_id in all_stories]
            selected_component_ids = set().union(*(story_component_ids(story) for story in selected_stories)) if selected_stories else set()
            flow_story_ids = [
                story_id
                for story_id in referenced_story_ids
                if isinstance(all_stories.get(story_id), dict) and (all_stories.get(story_id) or {}).get("flows")
            ]
            if require_flow_story and not flow_story_ids:
                hotspot_refs: list[str] = []
                for root_id in selected_roots or preferred_root_ids:
                    for fact in control_hotspots_by_component.get(root_id, []):
                        for source in fact.get("source_files") or []:
                            source = str(source)
                            if source and source not in hotspot_refs:
                                hotspot_refs.append(source)
                issues.append(
                    {
                        "level": "WARNING",
                        "section": "narrative",
                        "kind": "narrative-selection",
                        "message": "system-overview does not include a clearly flow-bearing story even though deterministic signals suggest the repo overview should teach the operating model through a real flow",
                        "conflict_type": "fact_vs_semantic",
                        "related_entities": [nid, *referenced_story_ids],
                        "evidence_refs": hotspot_refs[:3],
                    }
                )
            hotspot_components = {
                str(item.get("component") or "")
                for item in preferred_flow_hotspots
                if str(item.get("component") or "")
            }
            if hotspot_components and selected_component_ids and selected_component_ids.isdisjoint(hotspot_components):
                hotspot_refs: list[str] = []
                for item in preferred_flow_hotspots[:3]:
                    for ref in item.get("source_files") or []:
                        ref = str(ref)
                        if ref and ref not in hotspot_refs:
                            hotspot_refs.append(ref)
                issues.append(
                    {
                        "level": "WARNING",
                        "section": "narrative",
                        "kind": "narrative-selection",
                        "message": "system-overview avoids the strongest deterministic control hotspots, so the repo overview may miss the repo's defining operating path",
                        "conflict_type": "fact_vs_semantic",
                        "related_entities": [nid, *sorted(hotspot_components)[:3]],
                        "evidence_refs": hotspot_refs[:3],
                    }
                )

            if require_state_or_boundary_story:
                has_state_or_boundary_story = False
                for story in selected_stories:
                    component_ids = story_component_ids(story)
                    if any(component in state_access_by_component for component in component_ids):
                        has_state_or_boundary_story = True
                        break
                    if any(str(step.get("to") or "") in state_ids for flow in story.get("flows") or [] for step in flow.get("steps") or [] if isinstance(step, dict)):
                        has_state_or_boundary_story = True
                        break
                if not has_state_or_boundary_story:
                    boundary_refs: list[str] = []
                    for root_id in selected_roots or preferred_root_ids:
                        for fact in state_access_by_component.get(root_id, []):
                            for source in fact.get("source_files") or []:
                                source = str(source)
                                if source and source not in boundary_refs:
                                    boundary_refs.append(source)
                    issues.append(
                        {
                            "level": "WARNING",
                            "section": "narrative",
                            "kind": "narrative-selection",
                        "message": "system-overview does not include a story that clearly teaches a state or dependency boundary even though deterministic evidence suggests one is central to the repo overview",
                            "conflict_type": "fact_vs_semantic",
                            "related_entities": [nid, *referenced_story_ids],
                            "evidence_refs": boundary_refs[:3],
                        }
                    )
                boundary_components = {
                    component
                    for item in preferred_boundary_targets
                    for component in (item.get("components") or [])
                    if component
                }
                if boundary_components and selected_component_ids and selected_component_ids.isdisjoint(boundary_components):
                    boundary_refs: list[str] = []
                    for item in preferred_boundary_targets[:3]:
                        for ref in item.get("source_files") or []:
                            ref = str(ref)
                            if ref and ref not in boundary_refs:
                                boundary_refs.append(ref)
                    issues.append(
                        {
                            "level": "WARNING",
                            "section": "narrative",
                            "kind": "narrative-selection",
                        "message": "system-overview avoids the strongest deterministic state or boundary targets, so the repo overview may miss an important system boundary",
                            "conflict_type": "fact_vs_semantic",
                            "related_entities": [nid, *sorted(boundary_components)[:3]],
                            "evidence_refs": boundary_refs[:3],
                        }
                    )

            if prefer_child_stories and referenced_story_ids:
                selected_child_story_ids = [story_id for story_id in referenced_story_ids if (all_stories.get(story_id) or {}).get("parent")]
                if not selected_child_story_ids and child_story_ids_by_parent:
                    issues.append(
                        {
                            "level": "WARNING",
                            "section": "narrative",
                            "kind": "narrative-selection",
                            "message": "system-overview stays root-only even though deterministic narrative seeds suggest a child story would teach the architecture more clearly",
                            "conflict_type": "fact_vs_semantic",
                            "related_entities": [nid, *referenced_story_ids],
                            "evidence_refs": [],
                        }
                    )

    present_optional_recommended = sorted(optional_recommended_ids & present_ids)
    if preferred_optional_target > 0 and len(present_optional_recommended) < preferred_optional_target and optional_recommended_records:
        missing_ranked = [
            item
            for item in optional_recommended_records
            if str(item.get("id") or "") not in present_ids
        ]
        if missing_ranked:
            preferred_missing = [str(item.get("id") or "") for item in missing_ranked[:preferred_optional_target]]
            issues.append(
                {
                    "level": "WARNING",
                    "section": "narrative",
                    "kind": "narrative-selection",
                    "message": (
                        "Deterministic narrative seeds suggest the repo is missing one of its strongest optional "
                        f"teaching paths: {', '.join(preferred_missing)}"
                    ),
                    "conflict_type": "fact_vs_semantic",
                    "related_entities": preferred_missing,
                    "evidence_refs": [],
                }
            )
    if optional_recommended_ids and not present_optional_recommended:
        record = optional_recommended_records[0] if optional_recommended_records else None
        exemplar_id = str((record or {}).get("id") or (sorted(optional_recommended_ids)[0] if optional_recommended_ids else ""))
        evidence_refs: list[str] = []
        evidence = (record or {}).get("evidence") or {}
        if isinstance(evidence, dict):
            for key in ("domains", "flow_hotspots", "targets", "concepts"):
                for value in evidence.get(key) or []:
                    if isinstance(value, str) and value and value not in evidence_refs:
                        evidence_refs.append(value)
        issues.append(
            {
                "level": "WARNING",
                "section": "narrative",
                "kind": "narrative-selection",
                "message": "Deterministic narrative seeds suggest the repo would benefit from at least one additional canonical narrative beyond system-overview, but none are present",
                "conflict_type": "fact_vs_semantic",
                "related_entities": sorted(optional_recommended_ids),
                "evidence_refs": evidence_refs[:3],
            }
        )

    return issues


def validate_meta(meta: dict, analysis_dir: Path) -> list[dict]:
    issues = []

    def error(msg):
        issues.append({"level": "ERROR", "section": "meta", "message": msg})

    def warn(msg):
        issues.append({"level": "WARNING", "section": "meta", "message": msg})

    required_fields = [
        "project",
        "analysis_id",
        "sha",
        "commit_time",
        "analysis_mode",
        "blast",
        "artifacts",
        "schemas",
    ]
    for field in required_fields:
        if field not in meta:
            error(f"meta.json missing required field: {field}")

    artifacts = meta.get("artifacts")
    if isinstance(artifacts, dict):
        def resolve_artifact_ref(value: str) -> Path:
            candidate = Path(value)
            return candidate if candidate.is_absolute() else (analysis_dir / candidate)

        for key, value in artifacts.items():
            if value and not isinstance(value, str):
                error(f"meta.json artifacts.{key} must be a string path when present")
        root = artifacts.get("root")
        if isinstance(root, str) and root:
            resolved_root = resolve_artifact_ref(root)
            if resolved_root != analysis_dir:
                warn(f"meta.json artifacts.root '{root}' does not match analysis dir '{analysis_dir}'")
    elif artifacts is not None:
        error("meta.json artifacts must be an object")

    schemas = meta.get("schemas")
    if isinstance(schemas, dict):
        for key, value in schemas.items():
            if not value:
                error(f"meta.json schemas.{key} is required")
            elif not isinstance(value, str) or not value.startswith("/"):
                error(f"meta.json schemas.{key} must be an absolute path")
    elif schemas is not None:
        error("meta.json schemas must be an object")

    validation = meta.get("validation")
    if validation is not None:
        if not isinstance(validation, dict):
            error("meta.json validation must be an object")
        else:
            attempts = validation.get("attempts")
            if attempts is not None and not isinstance(attempts, int):
                error("meta.json validation.attempts must be an integer")
            passed = validation.get("passed")
            if passed is not None and not isinstance(passed, bool):
                error("meta.json validation.passed must be a boolean")
            token = validation.get("token")
            if token is not None and not isinstance(token, str):
                error("meta.json validation.token must be a string")

    return issues


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
    if section == "narrative" and ("teaching goals" in message or "served by the selected stories" in message or "missing `teaches`" in message):
        return "narrative-coherence"
    if "cycle" in message:
        return "graph-cycle"
    if section == "state" and ("too narrow" in message or "persistence" in message):
        return "state-truthfulness"
    if section == "concepts":
        return "concept-evidence"
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


def summarize_issues(issues: list[dict]) -> dict:
    by_level = Counter(str(issue.get("level") or "") for issue in issues)
    by_kind = Counter(classify_issue_kind(issue) for issue in issues)
    by_family = Counter(issue_family(issue) for issue in issues)
    semantic_conflicts = sum(1 for issue in issues if is_semantic_conflict(issue))
    return {
        "by_level": dict(sorted(by_level.items())),
        "by_kind": dict(sorted(by_kind.items())),
        "by_family": dict(sorted(by_family.items())),
        "semantic_conflict_count": semantic_conflicts,
    }


def issue_family(issue: dict) -> str:
    kind = classify_issue_kind(issue)
    if kind in {"path-provenance", "concept-evidence"}:
        return "provenance"
    if kind in {"grounding"}:
        return "grounding"
    if kind in {"health-criteria-missing", "health-scenario-link-missing", "health-scenario-link-invalid", "health-ownership-unclear", "failure-scenario-missing", "health-model", "monitoring-model", "gaps-model"}:
        return "health-model"
    if kind in {"story-decomposition", "narrative-selection", "narrative-overview", "narrative-coherence", "narrative-count", "story-quality"}:
        return "teaching-structure"
    if kind in {"graph-cycle", "state-truthfulness", "component-model", "flow-model", "framework-resolution", "actors-model", "events-model", "domain-model", "dependency-model"}:
        return "semantic-consistency"
    if str(issue.get("section") or "") == "structure":
        return "artifact-structure"
    return "general"


def is_semantic_conflict(issue: dict) -> bool:
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
        "concept-evidence",
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
        "state-truthfulness": "fact_vs_semantic",
        "story-decomposition": "shape_tension",
        "narrative-selection": "cross_artifact",
        "narrative-overview": "cross_artifact",
        "narrative-coherence": "cross_artifact",
        "narrative-count": "shape_tension",
        "component-model": "cross_artifact",
        "flow-model": "cross_artifact",
        "concept-evidence": "fact_vs_semantic",
        "framework-resolution": "fact_vs_semantic",
        "health-criteria-missing": "cross_artifact",
        "health-scenario-link-missing": "fact_vs_semantic",
        "health-scenario-link-invalid": "cross_artifact",
        "health-ownership-unclear": "shape_tension",
        "failure-scenario-missing": "fact_vs_semantic",
        "health-model": "cross_artifact",
        "monitoring-model": "cross_artifact",
        "gaps-model": "cross_artifact",
        "actors-model": "fact_vs_semantic",
        "events-model": "fact_vs_semantic",
        "domain-model": "fact_vs_semantic",
        "dependency-model": "cross_artifact",
    }
    return mapping.get(kind)


def issue_priority(issue: dict) -> str:
    if str(issue.get("level") or "") == "ERROR":
        return "high"
    kind = classify_issue_kind(issue)
    if kind in {"graph-cycle", "state-truthfulness", "component-model", "flow-model", "path-provenance", "concept-evidence", "health-model", "dependency-model", "monitoring-model", "gaps-model", "health-scenario-link-invalid"}:
        return "high"
    if kind in {"framework-resolution", "health-criteria-missing", "health-scenario-link-missing", "health-ownership-unclear", "failure-scenario-missing", "actors-model", "events-model", "domain-model"}:
        return "medium"
    if kind in {"story-decomposition", "narrative-selection", "narrative-overview", "narrative-coherence", "narrative-count", "story-quality"}:
        return "medium"
    return "low"


def recommended_artifacts(issue: dict) -> list[str]:
    kind = classify_issue_kind(issue)
    mapping = {
        "grounding": ["facts/symbols-seed.json"],
        "state-truthfulness": ["facts/state-seeds.json"],
        "story-decomposition": ["facts/story-seeds.json", "facts/component-seeds.json", "facts/narrative-seeds.json", "facts/state-access-summary.json"],
        "narrative-selection": ["facts/story-seeds.json", "facts/component-seeds.json", "facts/narrative-seeds.json", "facts/control-hotspots.json", "facts/state-access-summary.json", "atlas.json"],
        "narrative-overview": ["facts/story-seeds.json", "facts/component-seeds.json", "facts/narrative-seeds.json", "facts/control-hotspots.json", "atlas.json"],
        "narrative-coherence": ["facts/story-seeds.json", "facts/component-seeds.json", "facts/narrative-seeds.json", "narratives.yaml", "atlas.json"],
        "narrative-count": ["facts/narrative-seeds.json", "narratives.yaml", "atlas.json"],
        "story-quality": ["facts/story-seeds.json", "facts/component-seeds.json"],
        "component-model": ["facts/component-seeds.json", "facts/story-seeds.json"],
        "flow-model": ["facts/symbols-seed.json", "facts/component-seeds.json"],
        "health-criteria-missing": ["facts/health-candidates.json", "atlas.json"],
        "health-scenario-link-missing": ["facts/failure-scenario-candidates.json", "atlas.json"],
        "health-scenario-link-invalid": ["atlas.json", "facts/failure-scenario-candidates.json"],
        "health-ownership-unclear": ["facts/component-seeds.json", "atlas.json"],
        "failure-scenario-missing": ["facts/failure-scenario-candidates.json", "facts/health-candidates.json", "atlas.json"],
        "health-model": ["facts/health-candidates.json", "atlas.json"],
        "monitoring-model": ["facts/health-candidates.json", "facts/failure-scenario-candidates.json", "atlas.json"],
        "gaps-model": ["facts/health-candidates.json", "facts/failure-scenario-candidates.json", "facts/concept-evidence.json", "atlas.json"],
        "actors-model": ["facts/routes.json", "facts/jobs.json", "facts/events.json", "atlas.json"],
        "events-model": ["facts/events.json", "atlas.json"],
        "domain-model": ["facts/models.json", "atlas.json"],
        "dependency-model": ["facts/external-clients.json", "atlas.json"],
        "concept-evidence": ["facts/concept-evidence.json"],
        "framework-resolution": ["facts/frameworks.json"],
        "path-provenance": ["facts/index.json", "facts/startup.json"],
    }
    return mapping.get(kind, [])


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
                "suggested_resolution": suggested_resolution(issue),
            },
        )
        bucket["issue_ids"].append(stable_issue_id(issue))
        bucket["issue_count"] += 1
        bucket["sections"].add(str(issue.get("section") or ""))
        if len(bucket["messages"]) < 3:
            bucket["messages"].append(str(issue.get("message") or ""))
        priorities = {"high": 3, "medium": 2, "low": 1}
        if priorities[issue_priority(issue)] > priorities[bucket["priority"]]:
            bucket["priority"] = issue_priority(issue)
    ordered = sorted(
        grouped.values(),
        key=lambda item: (
            {"high": 0, "medium": 1, "low": 2}.get(item["priority"], 3),
            -item["issue_count"],
            item["label"],
        ),
    )
    result = []
    for item in ordered[:12]:
        result.append(
            {
                "id": item["id"],
                "priority": item["priority"],
                "family": item["family"],
                "kind": item["kind"],
                "label": item["label"],
                "issue_count": item["issue_count"],
                "sections": sorted(section for section in item["sections"] if section),
                "issue_ids": item["issue_ids"],
                "messages": item["messages"],
                "recommended_artifacts": sorted({artifact for issue in issues if stable_issue_id(issue) in item["issue_ids"] for artifact in recommended_artifacts(issue)}),
                "suggested_resolution": item["suggested_resolution"],
            }
        )
    return result


def load_repair_log(path: Path) -> dict:
    if not path.exists():
        return {"version": "1", "iterations": []}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(payload, dict) and isinstance(payload.get("iterations"), list):
            payload.setdefault("version", "1")
            return payload
    except json.JSONDecodeError:
        pass
    return {"version": "1", "iterations": []}


def append_repair_log(path: Path, analysis_dir: Path, valid: bool, issues: list[dict]) -> None:
    payload = load_repair_log(path)
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
            first_seen = previous_open[issue_id].get("first_seen_iteration") or (len(iterations) or 1)
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
                "is_semantic_conflict": is_semantic_conflict(issue),
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
                "is_semantic_conflict": prior.get("is_semantic_conflict", False),
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
        "open_semantic_conflicts": sum(1 for issue in issues if is_semantic_conflict(issue)),
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
            ("semantic_conflicts_remaining", conflict_summary["open_semantic_conflicts"] > 0),
            ("warning_volume_still_actionable", sum(1 for issue in issues if issue.get("level") == "WARNING") > 5 and len(repair_targets) <= 5),
        )
        if triggered
    ]
    iteration = {
        "iteration": len(iterations) + 1,
        "timestamp": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "status": "needs_refinement" if valid and quality_gate_reasons else ("valid" if valid else "invalid"),
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
        "concept-evidence": "Repair the concept evidence files or component references so provenance is valid.",
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


def load_yaml(path: Path) -> dict | None:
    """Load YAML, falling back to simple parsing if PyYAML not available."""
    if yaml:
        try:
            return yaml.safe_load(path.read_text())
        except Exception:
            return None
    else:
        # Minimal fallback: try JSON (some "YAML" files might be JSON)
        try:
            return json.loads(path.read_text())
        except Exception:
            return None


def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <analysis-dir> [--lock]")
        sys.exit(2)

    analysis_dir = Path(sys.argv[1])
    use_lock = os.environ.get("VALIDATE_LOCK") == "1"
    lock_path = analysis_dir / ".validate-lock"
    repair_log_path = analysis_dir / "repair-log.json"

    if not analysis_dir.exists():
        print(f"Directory not found: {analysis_dir}")
        sys.exit(2)

    all_issues = []

    # Derive project root from analysis dir path.
    # Expected: /kord/agents/<agent>/memory/projects/<project>/analysis/<analysis-id>/
    # Project code should resolve from one canonical shared-PVC repo root.
    project_root = None
    explicit_project_root = os.environ.get("AUGUR_PROJECT_ROOT", "").strip()
    if explicit_project_root:
        explicit_candidate = Path(explicit_project_root)
        if explicit_candidate.exists():
            project_root = explicit_candidate

    if project_root is None and "projects" in analysis_dir.parts:
        proj_idx = analysis_dir.parts.index("projects")
        if proj_idx + 1 < len(analysis_dir.parts):
            project_name = analysis_dir.parts[proj_idx + 1]
            configured_root = os.environ.get("PROJECTS_ROOT", "").strip()
            candidate_roots = []
            if configured_root:
                candidate_roots.append(Path(configured_root))
            candidate_roots.extend([
                Path("/kord/shared/repos"),
                Path("/kord/repos"),
            ])
            seen_roots: set[Path] = set()
            for projects_root in candidate_roots:
                if projects_root in seen_roots:
                    continue
                seen_roots.add(projects_root)
                candidate = projects_root / project_name
                if candidate.exists():
                    project_root = candidate
                    break

    # --- Deterministic artifacts ---
    blast_path = analysis_dir / "blast.json"
    if not blast_path.exists():
        all_issues.append({"level": "ERROR", "section": "structure", "message": f"blast.json not found at {blast_path}. Write blast radius output to this exact path."})
    else:
        try:
            json.loads(blast_path.read_text())
        except json.JSONDecodeError as e:
            all_issues.append({"level": "ERROR", "section": "blast", "message": f"JSON parse error: {e}"})

    facts_dir = analysis_dir / "facts"
    if not facts_dir.exists():
        all_issues.append({"level": "ERROR", "section": "structure", "message": f"facts/ directory not found at {facts_dir}. Write deterministic fact outputs here."})
    elif not facts_dir.is_dir():
        all_issues.append({"level": "ERROR", "section": "structure", "message": f"facts path exists but is not a directory: {facts_dir}"})

    concepts_path = facts_dir / "concept-evidence.json"
    concepts_payload = {}
    if concepts_path.exists():
        try:
            concepts_payload = json.loads(concepts_path.read_text())
        except json.JSONDecodeError as e:
            all_issues.append({"level": "ERROR", "section": "concept-evidence", "message": f"JSON parse error: {e}"})

    frameworks_path = facts_dir / "frameworks.json"
    frameworks_payload = {}
    if frameworks_path.exists():
        try:
            frameworks_payload = json.loads(frameworks_path.read_text())
        except json.JSONDecodeError as e:
            all_issues.append({"level": "ERROR", "section": "frameworks", "message": f"JSON parse error: {e}"})

    component_seeds_path = facts_dir / "component-seeds.json"
    component_seeds_payload = {}
    if component_seeds_path.exists():
        try:
            component_seeds_payload = json.loads(component_seeds_path.read_text())
        except json.JSONDecodeError as e:
            all_issues.append({"level": "ERROR", "section": "component-seeds", "message": f"JSON parse error: {e}"})

    story_seeds_path = facts_dir / "story-seeds.json"
    story_seeds_payload = {}
    if story_seeds_path.exists():
        try:
            story_seeds_payload = json.loads(story_seeds_path.read_text())
        except json.JSONDecodeError as e:
            all_issues.append({"level": "ERROR", "section": "story-seeds", "message": f"JSON parse error: {e}"})
    story_seed_refs: list[str] = []
    if story_seeds_payload:
        raw_story_seed_refs = [
            *[str(item) for item in (story_seeds_payload.get("starter_files") or []) if item],
            *[str(item) for item in (story_seeds_payload.get("hot_files") or []) if item],
        ]
        seen_story_seed_refs: set[str] = set()
        for ref in raw_story_seed_refs:
            normalized = normalize_rel_path(ref)
            if normalized and normalized not in seen_story_seed_refs:
                seen_story_seed_refs.add(normalized)
                story_seed_refs.append(normalized)

    narrative_seeds_path = facts_dir / "narrative-seeds.json"
    narrative_seeds_payload = {}
    if narrative_seeds_path.exists():
        try:
            narrative_seeds_payload = json.loads(narrative_seeds_path.read_text())
        except json.JSONDecodeError as e:
            all_issues.append({"level": "ERROR", "section": "narrative-seeds", "message": f"JSON parse error: {e}"})

    health_candidates_path = facts_dir / "health-candidates.json"
    health_candidates_payload = {}
    if health_candidates_path.exists():
        try:
            health_candidates_payload = json.loads(health_candidates_path.read_text())
        except json.JSONDecodeError as e:
            all_issues.append({"level": "ERROR", "section": "health-candidates", "message": f"JSON parse error: {e}"})

    control_hotspots_path = facts_dir / "control-hotspots.json"
    control_hotspots_payload = {}
    if control_hotspots_path.exists():
        try:
            control_hotspots_payload = json.loads(control_hotspots_path.read_text())
        except json.JSONDecodeError as e:
            all_issues.append({"level": "ERROR", "section": "control-hotspots", "message": f"JSON parse error: {e}"})

    state_access_summary_path = facts_dir / "state-access-summary.json"
    state_access_summary_payload = {}
    if state_access_summary_path.exists():
        try:
            state_access_summary_payload = json.loads(state_access_summary_path.read_text())
        except json.JSONDecodeError as e:
            all_issues.append({"level": "ERROR", "section": "state-access-summary", "message": f"JSON parse error: {e}"})

    atlas_node_ids = set()
    atlas_entity_ids = set()
    atlas = {}
    if not DETERMINISTIC_ONLY:
        # --- Atlas ---
        atlas_path = analysis_dir / "atlas.json"

        if not atlas_path.exists():
            all_issues.append({"level": "ERROR", "section": "structure", "message": f"atlas.json not found at {atlas_path}. Write your semantic atlas to this exact path."})
        elif atlas_path.suffix != ".json":
            all_issues.append({"level": "ERROR", "section": "structure", "message": f"atlas should be .json, got {atlas_path.suffix}"})
        else:
            try:
                atlas = json.loads(atlas_path.read_text())
                issues, atlas_node_ids, atlas_entity_ids = validate_atlas(
                    atlas,
                    project_root,
                    analysis_dir,
                    concepts_payload,
                    frameworks_payload,
                    health_candidates_payload,
                )
                all_issues.extend(issues)
            except json.JSONDecodeError as e:
                all_issues.append({"level": "ERROR", "section": "atlas", "message": f"JSON parse error: {e}"})

        if atlas and component_seeds_payload:
            top_level_components = [
                component for component in (atlas.get("components") or [])
                if isinstance(component, dict) and not component.get("parent")
            ]
            for seed in component_seeds_payload.get("candidate_components") or []:
                if not isinstance(seed, dict):
                    continue
                root_likelihood = int(seed.get("root_likelihood") or 0)
                if root_likelihood < 6:
                    continue
                representative_files = [str(item) for item in (seed.get("representative_files") or []) if item]
                if not representative_files:
                    continue
                seed_id = str(seed.get("id") or "")
                group = str(seed.get("group") or seed_id or "seed")
                matched = False
                for component in top_level_components:
                    component_id = str(component.get("id") or "")
                    component_name = str(component.get("name") or "")
                    modules = [str(item) for item in (component.get("modules") or []) if item]
                    if seed_id and seed_id in {component_id, component_name.lower().replace(" ", "-")}:
                        matched = True
                        break
                    if any(path_matches_prefix(module, candidate) for module in modules for candidate in representative_files):
                        matched = True
                        break
                if not matched:
                    all_issues.append({
                        "level": "WARNING",
                        "section": "components",
                        "kind": "component-model",
                        "message": f"Strong deterministic component seed '{group}' is not clearly represented by a top-level component",
                        "related_entities": [seed_id] if seed_id else [],
                        "evidence_refs": representative_files[:3],
                        "conflict_type": "fact_vs_semantic",
                    })

    story_ids = set()
    all_stories: dict[str, dict] = {}
    narratives: list[dict] = []
    if not DETERMINISTIC_ONLY:
        component_signal_counts: dict[str, int] = {}
        atlas_story_node_details: dict[str, dict] = {}
        if isinstance(atlas, dict):
            component_ids = {
                str(component.get("id"))
                for component in (atlas.get("components") or [])
                if isinstance(component, dict) and component.get("id")
            }
            for component in atlas.get("components") or []:
                if isinstance(component, dict) and component.get("id"):
                    atlas_story_node_details[str(component.get("id"))] = {
                        "kind": "component",
                        "description": component.get("description"),
                        "summary": component.get("summary"),
                    }
            for dependency in atlas.get("external_dependencies") or []:
                if isinstance(dependency, dict) and dependency.get("id"):
                    atlas_story_node_details[str(dependency.get("id"))] = {
                        "kind": "external dependency",
                        "description": dependency.get("description"),
                        "summary": dependency.get("summary"),
                    }
            for flow in atlas.get("flows") or []:
                if not isinstance(flow, dict):
                    continue
                for step in flow.get("steps") or []:
                    if isinstance(step, dict):
                        component = str(step.get("component") or "")
                        if component in component_ids:
                            component_signal_counts[component] = component_signal_counts.get(component, 0) + 1
            for state in atlas.get("state") or []:
                if isinstance(state, dict):
                    component = str(state.get("component") or "")
                    if component in component_ids:
                        component_signal_counts[component] = component_signal_counts.get(component, 0) + 1
            for dependency in atlas.get("external_dependencies") or []:
                if not isinstance(dependency, dict):
                    continue
                for component in dependency.get("components") or []:
                    component = str(component or "")
                    if component in component_ids:
                        component_signal_counts[component] = component_signal_counts.get(component, 0) + 1

        # --- Stories ---
        stories_dir = analysis_dir / "stories"

        if not stories_dir.exists():
            all_issues.append({"level": "ERROR", "section": "structure", "message": f"stories/ directory not found at {stories_dir}. Write each story as a separate .yaml file in this directory."})
        else:
            for f in sorted(stories_dir.iterdir()):
                if f.suffix == ".md":
                    all_issues.append({"level": "ERROR", "section": "structure", "message": f"Story file is .md (should be .yaml): {f.name}"})
                    continue
                if f.suffix not in (".yaml", ".yml"):
                    continue
                story = load_yaml(f)
                if story is None:
                    all_issues.append({"level": "ERROR", "section": "story", "message": f"Failed to parse: {f.name}"})
                    continue
                sid = story.get("id", f.stem)
                story_ids.add(sid)
                all_issues.extend(validate_story(
                    story,
                    atlas_node_ids,
                    atlas_entity_ids,
                    atlas_story_node_details,
                    project_root,
                    analysis_dir,
                ))

            # Story tree: check children per parent
            for f in sorted(stories_dir.iterdir()):
                if f.suffix not in (".yaml", ".yml"):
                    continue
                story = load_yaml(f)
                if story:
                    all_stories[story.get("id", f.stem)] = story

            children_count = {}
            for sid, story in all_stories.items():
                parent = story.get("parent")
                if parent:
                    children_count[parent] = children_count.get(parent, 0) + 1

            for parent_id, count in children_count.items():
                if count > 5:
                    all_issues.append({"level": "ERROR", "section": "story",
                        "message": f"Story '{parent_id}' has {count} children (max 5). Consolidate child stories."})
                elif count < 2:
                    all_issues.append({
                        "level": "WARNING",
                        "section": "story",
                        "kind": "story-decomposition",
                        "message": f"Story '{parent_id}' has {count} child (preferred 2+). Add another distinct concern or merge the child back into the parent.",
                        "related_entities": [parent_id],
                        "evidence_refs": story_seed_refs[:3],
                    })
                if count < 2 and component_signal_counts.get(parent_id, 0) >= 4:
                    all_issues.append({
                        "level": "WARNING",
                        "section": "story",
                        "kind": "story-decomposition",
                        "message": f"Story '{parent_id}' looks under-decomposed for a root with multiple flows/state/dependencies. Draft more concern-focused children before finalizing.",
                        "related_entities": [parent_id],
                        "evidence_refs": story_seed_refs[:3],
                        "conflict_type": "fact_vs_semantic" if story_seed_refs else None,
                    })

            root_story_count = sum(1 for story in all_stories.values() if not story.get("parent"))
            if root_story_count < 3:
                all_issues.append({"level": "ERROR", "section": "story",
                    "message": f"Too few root stories: {root_story_count} (minimum 3, one per top-level component)"})
            elif root_story_count > 5:
                all_issues.append({"level": "ERROR", "section": "story",
                    "message": f"Too many root stories: {root_story_count} (maximum 5, one per top-level component)"})

            if all_stories and not children_count and len(all_stories) >= 4:
                all_issues.append({
                    "level": "ERROR",
                    "section": "story",
                    "kind": "story-decomposition",
                    "message": "Story tree is fully flat. Add child stories when root stories contain distinct nested concerns.",
                    "related_entities": sorted(all_stories.keys()),
                    "evidence_refs": story_seed_refs[:3],
                    "conflict_type": "fact_vs_semantic" if story_seed_refs else None,
                })

        # --- Narratives ---
        narratives_path = analysis_dir / "narratives.yaml"
        if not narratives_path.exists():
            all_issues.append({"level": "ERROR", "section": "structure", "message": f"narratives.yaml not found at {narratives_path}. Write cross-cutting story sequences here."})
        else:
            narratives_doc = load_yaml(narratives_path)
            if narratives_doc is None:
                all_issues.append({"level": "ERROR", "section": "narrative", "message": f"Failed to parse: {narratives_path.name}"})
            else:
                if not isinstance(narratives_doc, dict):
                    all_issues.append({"level": "ERROR", "section": "narrative", "message": "narratives.yaml must be a mapping with top-level version and narratives keys"})
                    narratives = []
                else:
                    version = narratives_doc.get("version")
                    if version != "1":
                        all_issues.append({"level": "ERROR", "section": "narrative", "message": f"narratives.yaml version must be '1', got '{version}'"})
                    narratives = narratives_doc.get("narratives", [])
                if not isinstance(narratives, list):
                    all_issues.append({"level": "ERROR", "section": "narrative", "message": "narratives.yaml must contain a top-level 'narratives' list"})
                else:
                    ids = set()
                    child_story_ids = {sid for sid, story in all_stories.items() if story.get("parent")}
                    if len(narratives) < 2:
                        all_issues.append({
                            "level": "WARNING",
                            "section": "narrative",
                            "kind": "narrative-count",
                            "message": "Only one narrative is present; most repos should provide at least one additional audience or cross-cutting reading path",
                        })
                    elif len(narratives) > 4:
                        all_issues.append({
                            "level": "WARNING",
                            "section": "narrative",
                            "kind": "narrative-count",
                            "message": f"{len(narratives)} narratives are present; usually keep a repo to 2-4 non-redundant narratives",
                        })
                    for narrative in narratives:
                        if not isinstance(narrative, dict):
                            all_issues.append({"level": "ERROR", "section": "narrative", "message": "narratives.yaml contains a non-object narrative entry"})
                            continue
                        nid = narrative.get("id", "")
                        if nid in ids:
                            all_issues.append({"level": "ERROR", "section": "narrative", "message": f"Duplicate narrative id '{nid}'"})
                        ids.add(nid)
                        all_issues.extend(validate_narrative(narrative, story_ids))
                        narrative_story_ids = {
                            (entry.get("id", "") if isinstance(entry, dict) else entry)
                            for entry in (narrative.get("stories", []) or [])
                        }
                        if child_story_ids and narrative_story_ids and narrative_story_ids.isdisjoint(child_story_ids):
                            all_issues.append({
                                "level": "WARNING",
                                "section": "narrative",
                                "kind": "narrative-selection",
                                "message": f"Narrative '{nid}' uses only root stories even though child stories exist. Prefer more specific child stories when they carry the real explanatory detail.",
                                "related_entities": [nid, *sorted(narrative_story_ids)],
                                "evidence_refs": story_seed_refs[:3],
                                "conflict_type": "fact_vs_semantic" if story_seed_refs else None,
                            })
                    if "system-overview" not in ids:
                        all_issues.append({"level": "ERROR", "section": "narrative", "message": "system-overview narrative is required — default repo overview path covering the main top-level components"})

        if atlas and all_stories and isinstance(narratives, list):
            all_issues.extend(
                detect_cross_artifact_conflicts(
                    atlas,
                    all_stories,
                    narratives,
                    narrative_seeds_payload=narrative_seeds_payload,
                    control_hotspots_payload=control_hotspots_payload,
                    state_access_summary_payload=state_access_summary_payload,
                )
            )

    meta_path = analysis_dir / "meta.json"
    if meta_path.exists():
        try:
            meta = json.loads(meta_path.read_text())
            if isinstance(meta, dict):
                all_issues.extend(validate_meta(meta, analysis_dir))
            else:
                all_issues.append({"level": "ERROR", "section": "meta", "message": "meta.json must be a JSON object"})
        except json.JSONDecodeError as e:
            all_issues.append({"level": "ERROR", "section": "meta", "message": f"JSON parse error: {e}"})

    # --- Summary ---
    errors = [i for i in all_issues if i["level"] == "ERROR"]
    warnings = [i for i in all_issues if i["level"] == "WARNING"]

    for i in all_issues:
        section = f" [{i['section']}]" if i.get("section") else ""
        print(f"{i['level']}{section}: {i['message']}")

    valid = len(errors) == 0
    append_repair_log(repair_log_path, analysis_dir, valid, all_issues)
    repair_log = load_repair_log(repair_log_path)
    latest_iteration = (repair_log.get("iterations") or [])[-1] if (repair_log.get("iterations") or []) else {}
    final_status = str(latest_iteration.get("status") or ("valid" if valid else "invalid"))
    banner = "VALID" if final_status == "valid" else ("NEEDS_REFINEMENT" if final_status == "needs_refinement" else "INVALID")
    print(f"\n{banner}: {len(errors)} errors, {len(warnings)} warnings")

    if not valid:
        print(f"\nExpected output structure at {analysis_dir}:")
        print(f"  {analysis_dir}/blast.json           — deterministic blast radius JSON")
        print(f"  {analysis_dir}/facts/               — normalized fact domain files")
        if not DETERMINISTIC_ONLY:
            print(f"  {analysis_dir}/atlas.json           — v4 JSON (see atlas-schema.md)")
            print(f"  {analysis_dir}/stories/*.yaml       — one YAML file per story")
            print(f"  {analysis_dir}/narratives.yaml      — cross-cutting story sequences")

    # Lock management
    if use_lock:
        if final_status == "valid":
            if lock_path.exists():
                lock_path.unlink()
                print(f"Lock removed: {lock_path}")
        else:
            lock_path.write_text(f"{len(errors)} errors\n")
            print(f"Lock created: {lock_path}")

    sys.exit(0 if final_status == "valid" else 1)


if __name__ == "__main__":
    main()
