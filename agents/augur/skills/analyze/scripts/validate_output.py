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
        - getting-started narrative exists
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
from collections import Counter
from datetime import datetime, UTC
import hashlib
from pathlib import Path
from typing import Iterable

try:
    import yaml
except ImportError:
    yaml = None

KEBAB_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")

REQUIRED_ATLAS_FIELDS = [
    "version", "generated", "project", "purpose",
    "components", "flows", "state",
    "external_dependencies", "concepts", "tensions"
]

DETERMINISTIC_ONLY = (
    os.getenv("AUGUR_DETERMINISTIC_ONLY") in ("1", "true", "TRUE", "yes", "YES")
)


def kebab_case(s: str) -> bool:
    return bool(KEBAB_RE.match(s))


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
    project_root: Path | None = None,
    analysis_dir: Path | None = None,
) -> list[dict]:
    issues = []
    if not isinstance(health, dict):
        return issues
    failure_modes = health.get("failure_modes") or []
    if not isinstance(failure_modes, list):
        issues.append({"level": "ERROR", "section": section, "message": f"'{item_id}' health.failure_modes must be a list"})
        return issues
    seen_ids: set[str] = set()
    for failure_mode in failure_modes:
        if not isinstance(failure_mode, dict):
            issues.append({"level": "ERROR", "section": section, "message": f"'{item_id}' health.failure_modes contains a non-object entry"})
            continue
        failure_id = str(failure_mode.get("id") or "")
        if not failure_id:
            issues.append({"level": "ERROR", "section": section, "message": f"'{item_id}' health failure mode is missing id"})
            continue
        if not kebab_case(failure_id):
            issues.append({"level": "ERROR", "section": section, "message": f"'{item_id}' health failure mode id not kebab-case: '{failure_id}'"})
        if failure_id in seen_ids:
            issues.append({"level": "ERROR", "section": section, "message": f"'{item_id}' has duplicate health failure mode id '{failure_id}'"})
        seen_ids.add(failure_id)
        grounded = failure_mode.get("grounded_in") or []
        if not grounded:
            issues.append({"level": "WARNING", "section": section, "message": f"'{item_id}' health failure mode '{failure_id}' has no grounded_in"})
        elif project_root or analysis_dir:
            issues.extend(check_grounded_in(grounded, project_root, analysis_dir, section, f"{item_id}/{failure_id}"))
    return issues


def validate_atlas(
    atlas: dict,
    project_root: Path | None = None,
    analysis_dir: Path | None = None,
    concept_evidence_payload: dict | None = None,
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
        issues.extend(validate_health(component.get("health"), "components", cid or "<component>", project_root, analysis_dir))

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
    all_node_ids = component_ids | actor_ids | ext_dep_ids | state_ids

    # depends_on
    def check_deps(comps):
        for c in comps:
            for dep in c.get("depends_on", []):
                if dep not in component_ids:
                    error(f"Component '{c.get('id')}' depends_on unknown '{dep}'", "components")

    check_deps(components)

    for component in components:
        cid = str(component.get("id") or "?")
        modules = component.get("modules") or []
        if modules and (project_root or analysis_dir):
            issues.extend(check_existing_paths(modules, project_root, analysis_dir, "components", cid, label="module"))

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
        issues.extend(validate_health(f.get("health"), "flows", fid or "<flow>", project_root, analysis_dir))
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
        for step in f.get("steps", []):
            for key in ("component", "to"):
                ref = step.get(key, "")
                if ref and ref not in all_node_ids:
                    error(f"Flow '{fid}' step {key} references unknown '{ref}'", "flows")

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
    for gap in concepts.get("gaps", []):
        gid = str(gap.get("id") or "?")
        for comp in gap.get("components", []):
            if comp not in all_node_ids:
                error(f"Gap '{gid}' references unknown component '{comp}'", "concepts")
        grounded_refs = gap.get("grounded_in") or []
        if grounded_refs and (project_root or analysis_dir):
            issues.extend(check_grounded_in(grounded_refs, project_root, analysis_dir, "concepts", gid))
            issues.extend(verify_grounding_quality(
                grounded_refs,
                " ".join(str(part) for part in (gap.get("relevance"), gap.get("recommendation")) if part),
                project_root,
                analysis_dir,
                "concepts",
                gid,
            ))
        evidence = gap.get("evidence") or {}
        files = evidence.get("files") or []
        if files and (project_root or analysis_dir):
            issues.extend(check_existing_paths(files, project_root, analysis_dir, "concepts", gid, label="evidence file"))

    # Tensions
    for tension in atlas.get("tensions", []):
        for comp in tension.get("components", []):
            if comp not in all_node_ids:
                error(f"Tension '{tension.get('id', '?')}' references unknown component '{comp}'", "tensions")

    # External dependency health
    for dependency in atlas.get("external_dependencies", []):
        did = dependency.get("id", "")
        issues.extend(validate_health(dependency.get("health"), "external_dependencies", did or "<dependency>", project_root, analysis_dir))

    concept_ids = {p.get("id") for p in concepts.get("detected_patterns", []) if p.get("id")}
    concept_ids |= {ap.get("id") for ap in concepts.get("detected_anti_patterns", []) if ap.get("id")}
    concept_ids |= {gap.get("id") for gap in concepts.get("gaps", []) if gap.get("id")}
    tension_ids = {t.get("id") for t in atlas.get("tensions", []) if t.get("id")}
    all_entity_ids = all_node_ids | flow_ids | event_ids | concept_ids | tension_ids

    return issues, all_node_ids, all_entity_ids


def validate_story(
    story: dict,
    atlas_node_ids: set,
    atlas_entity_ids: set,
    project_root: Path | None = None,
    analysis_dir: Path | None = None,
) -> list[dict]:
    issues = []

    def error(msg):
        issues.append({"level": "ERROR", "section": "story", "message": msg})

    def warn(msg):
        issues.append({"level": "WARNING", "section": "story", "message": msg})

    sid = story.get("id", "<unknown>")
    parent_story = story.get("parent")

    if "id" not in story:
        error(f"Story missing required field: id")
    if "title" not in story:
        error(f"Story '{sid}' missing required field: title")
    if "teaches" not in story:
        error(f"Story '{sid}' missing required field: teaches")
    if "summary" not in story:
        error(f"Story '{sid}' missing required field: summary")

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

    # Bold refs in summary should resolve to atlas entities, not filenames or fact artifacts.
    bold_refs = re.findall(r"\*\*([^*]+)\*\*", summary)
    for ref in bold_refs:
        ref_kebab = ref.lower().replace(" ", "-")
        if ref_kebab not in atlas_entity_ids and ref not in atlas_entity_ids:
            error(f"Story '{sid}' bold ref '**{ref}**' doesn't match any atlas entity")

    # Structure node refs
    for struct in story.get("structures", []):
        for node in struct.get("nodes", []):
            nid = node.get("id", "") if isinstance(node, dict) else node
            if nid and nid not in atlas_node_ids:
                error(f"Story '{sid}' structure node '{nid}' not in atlas")
        for edge in struct.get("edges", []):
            for key in ("from", "to"):
                ref = edge.get(key, "")
                if ref and ref not in atlas_node_ids:
                    error(f"Story '{sid}' structure edge {key} '{ref}' not in atlas")

    # Flow node refs
    for flow in story.get("flows", []):
        for step in flow.get("steps", []):
            for key in ("node", "to"):
                ref = step.get(key, "")
                if ref and ref not in atlas_node_ids:
                    error(f"Story '{sid}' flow step {key} '{ref}' not in atlas")

    # Observation grounded_in
    for obs in story.get("observations", []):
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

    if parent_story:
        child_nodes: set[str] = set()
        for struct in story.get("structures", []):
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

    stories = narrative.get("stories", [])
    if len(stories) < 3:
        warn(f"Narrative '{jid}' has {len(stories)} stories (minimum 3)")
    elif len(stories) > 8:
        warn(f"Narrative '{jid}' has {len(stories)} stories (maximum 8)")

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
) -> list[dict]:
    issues: list[dict] = []
    components = {
        str(component.get("id")): component
        for component in (atlas.get("components") or [])
        if isinstance(component, dict) and component.get("id")
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
                    "message": (
                        f"Narrative '{nid}' uses root stories {', '.join(sorted(missing_child_coverage))} "
                        "without any of their more specific child stories"
                    ),
                    "conflict_type": "cross_artifact",
                    "related_entities": [nid, *sorted(missing_child_coverage)],
                    "evidence_refs": [],
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
        for key, value in artifacts.items():
            if value and (not isinstance(value, str) or not value.startswith("/")):
                error(f"meta.json artifacts.{key} must be an absolute path when present")
        root = artifacts.get("root")
        if isinstance(root, str) and root and root != str(analysis_dir):
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
    if kind in {"story-decomposition", "narrative-selection", "story-quality"}:
        return "teaching-structure"
    if kind in {"graph-cycle", "state-truthfulness", "component-model", "flow-model"}:
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
        "component-model",
        "flow-model",
        "concept-evidence",
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
        "component-model": "cross_artifact",
        "flow-model": "cross_artifact",
        "concept-evidence": "fact_vs_semantic",
    }
    return mapping.get(kind)


def issue_priority(issue: dict) -> str:
    if str(issue.get("level") or "") == "ERROR":
        return "high"
    kind = classify_issue_kind(issue)
    if kind in {"graph-cycle", "state-truthfulness", "component-model", "flow-model", "path-provenance", "concept-evidence"}:
        return "high"
    if kind in {"story-decomposition", "narrative-selection", "story-quality"}:
        return "medium"
    return "low"


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
        "story-decomposition": "Split the root into distinct concern-focused child stories or merge the weak child back.",
        "narrative-selection": "Use the more specific child stories when they carry the real explanatory detail.",
        "graph-cycle": "Revisit dependency direction and remove cyclic component relationships.",
        "state-truthfulness": "Widen the state label or persistence mode so it matches the configured backend reality.",
        "concept-evidence": "Repair the concept evidence files or component references so provenance is valid.",
        "component-model": "Refine the component graph so ids, parents, dependencies, and module paths are truthful.",
        "flow-model": "Tighten the flow description, references, or grounding so it matches the implementation path.",
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
                issues, atlas_node_ids, atlas_entity_ids = validate_atlas(atlas, project_root, analysis_dir, concepts_payload)
                all_issues.extend(issues)
            except json.JSONDecodeError as e:
                all_issues.append({"level": "ERROR", "section": "atlas", "message": f"JSON parse error: {e}"})

    story_ids = set()
    all_stories: dict[str, dict] = {}
    narratives: list[dict] = []
    if not DETERMINISTIC_ONLY:
        component_signal_counts: dict[str, int] = {}
        if isinstance(atlas, dict):
            component_ids = {
                str(component.get("id"))
                for component in (atlas.get("components") or [])
                if isinstance(component, dict) and component.get("id")
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
                all_issues.extend(validate_story(story, atlas_node_ids, atlas_entity_ids, project_root, analysis_dir))

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
                    all_issues.append({"level": "WARNING", "section": "story",
                        "message": f"Story '{parent_id}' has {count} child (preferred 2+). Add another distinct concern or merge the child back into the parent."})
                if count < 2 and component_signal_counts.get(parent_id, 0) >= 4:
                    all_issues.append({"level": "WARNING", "section": "story",
                        "message": f"Story '{parent_id}' looks under-decomposed for a root with multiple flows/state/dependencies. Draft more concern-focused children before finalizing."})

            root_story_count = sum(1 for story in all_stories.values() if not story.get("parent"))
            if root_story_count < 3:
                all_issues.append({"level": "ERROR", "section": "story",
                    "message": f"Too few root stories: {root_story_count} (minimum 3, one per top-level component)"})
            elif root_story_count > 5:
                all_issues.append({"level": "ERROR", "section": "story",
                    "message": f"Too many root stories: {root_story_count} (maximum 5, one per top-level component)"})

            if all_stories and not children_count and len(all_stories) >= 4:
                all_issues.append({"level": "ERROR", "section": "story",
                    "message": "Story tree is fully flat. Add child stories when root stories contain distinct nested concerns."})

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
                            all_issues.append({"level": "WARNING", "section": "narrative",
                                "message": f"Narrative '{nid}' uses only root stories even though child stories exist. Prefer more specific child stories when they carry the real explanatory detail."})
                    if "getting-started" not in ids:
                        all_issues.append({"level": "ERROR", "section": "narrative", "message": "getting-started narrative is required — teaching-order path covering the main top-level components"})

        if atlas and all_stories and isinstance(narratives, list):
            all_issues.extend(detect_cross_artifact_conflicts(atlas, all_stories, narratives))

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
