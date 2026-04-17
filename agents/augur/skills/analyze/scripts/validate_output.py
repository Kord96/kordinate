#!/usr/bin/env python3
"""Validate Augur analysis output for deterministic and semantic phases.

Usage:
    python validate_output.py <analysis-dir>

    <analysis-dir> is the validated Augur analysis directory.
    Deterministic-only runs must contain blast.json, facts/, and facts/concept-evidence.json.
    Full semantic runs must also contain atlas.json, stories/, and narratives.yaml.
    meta.json is validated when present, but it may be finalized after semantic validation.
    e.g., /kord/augur/memory/projects/<project>/analysis/<analysis-id>/

Lock management is automatic when VALIDATE_LOCK=1 is set in the environment.
This is used by the hook infrastructure, not by the agent directly.

Checks:
    Phase 1 deterministic:
        - blast.json exists and is valid JSON
        - facts/ exists and contains extracted domain files
        - facts/concept-evidence.json exists and is valid JSON

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
        - blast.json and facts/concept-evidence.json are JSON
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
from pathlib import Path

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

FORBIDDEN_LEGACY_ATLAS_FIELDS = [
    "groups",
    "stack",
    "debt",
    "api_surface",
    "security",
    "developer_experience",
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


def validate_atlas(atlas: dict, project_root: Path | None = None, analysis_dir: Path | None = None) -> list[dict]:
    issues = []

    def error(msg, section=""):
        issues.append({"level": "ERROR", "section": section, "message": msg})

    def warn(msg, section=""):
        issues.append({"level": "WARNING", "section": section, "message": msg})

    # Required fields
    for field in REQUIRED_ATLAS_FIELDS:
        if field not in atlas:
            error(f"Missing required field: {field}", "atlas")

    for field in FORBIDDEN_LEGACY_ATLAS_FIELDS:
        if field in atlas:
            error(f"Legacy field '{field}' must not appear in atlas.json", "atlas")

    # Version
    if atlas.get("version") != "4":
        error(f"Expected version '4', got '{atlas.get('version')}'", "atlas")

    # Components
    components = atlas.get("components", [])
    if len(components) < 4:
        warn(f"Few components: {len(components)} (expected 5-10)", "components")
    elif len(components) > 12:
        warn(f"Many components: {len(components)} (expected 5-10)", "components")

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
    if len(root_components) < 3:
        error(f"Too few top-level components: {len(root_components)} (minimum 3)", "components")
    elif len(root_components) > 5:
        error(f"Too many top-level components: {len(root_components)} (maximum 5)", "components")

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

    # Flows
    for f in atlas.get("flows", []):
        fid = f.get("id", "")
        if not f.get("grounded_in"):
            warn(f"Flow '{fid}' has no grounded_in", "flows")
        elif project_root or analysis_dir:
            issues.extend(check_grounded_in(f["grounded_in"], project_root, analysis_dir, "flows", fid))
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

    # Concepts
    concepts = atlas.get("concepts", {})
    for p in concepts.get("detected_patterns", []):
        for comp in p.get("components", []):
            if comp not in all_node_ids:
                error(f"Pattern '{p.get('id')}' references unknown component '{comp}'", "concepts")
    for ap in concepts.get("detected_anti_patterns", []):
        for comp in ap.get("components", []):
            if comp not in all_node_ids:
                error(f"Anti-pattern '{ap.get('id')}' references unknown component '{comp}'", "concepts")

    # Tensions
    for tension in atlas.get("tensions", []):
        for comp in tension.get("components", []):
            if comp not in all_node_ids:
                error(f"Tension '{tension.get('id', '?')}' references unknown component '{comp}'", "tensions")

    # External dependency health
    for dependency in atlas.get("external_dependencies", []):
        did = dependency.get("id", "")
        issues.extend(validate_health(dependency.get("health"), "external_dependencies", did or "<dependency>", project_root, analysis_dir))

    flow_ids = {f.get("id") for f in atlas.get("flows", []) if f.get("id")}
    event_ids = {e.get("id") for e in atlas.get("events", []) if e.get("id")}
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
        if not obs.get("grounded_in"):
            warn(f"Story '{sid}' observation '{oid}' has no grounded_in")
        elif project_root or analysis_dir:
            issues.extend(check_grounded_in(obs["grounded_in"], project_root, analysis_dir, "story", f"{sid}/{oid}"))
        comp = obs.get("component", "")
        if comp and comp not in atlas_node_ids:
            error(f"Story '{sid}' observation component '{comp}' not in atlas")

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
            projects_root = Path(os.environ.get("PROJECTS_ROOT", "/kord/repos"))
            candidate = projects_root / project_name
            if candidate.exists():
                project_root = candidate

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
    if not concepts_path.exists():
        all_issues.append({"level": "ERROR", "section": "structure", "message": f"facts/concept-evidence.json not found at {concepts_path}. Write deterministic concept evidence facts to this exact path."})
    else:
        try:
            json.loads(concepts_path.read_text())
        except json.JSONDecodeError as e:
            all_issues.append({"level": "ERROR", "section": "concept-evidence", "message": f"JSON parse error: {e}"})

    atlas_node_ids = set()
    atlas_entity_ids = set()
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
                issues, atlas_node_ids, atlas_entity_ids = validate_atlas(atlas, project_root, analysis_dir)
                all_issues.extend(issues)
            except json.JSONDecodeError as e:
                all_issues.append({"level": "ERROR", "section": "atlas", "message": f"JSON parse error: {e}"})

    story_ids = set()
    if not DETERMINISTIC_ONLY:
        journeys_dir = analysis_dir / "journeys"
        if journeys_dir.exists():
            all_issues.append({"level": "ERROR", "section": "structure", "message": f"Legacy journeys/ directory must not appear at {journeys_dir}. Use narratives.yaml instead."})

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
            all_stories = {}
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
                        "message": f"Story '{parent_id}' has {count} child (min 2). Add more or merge into parent."})

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
                    for narrative in narratives:
                        if not isinstance(narrative, dict):
                            all_issues.append({"level": "ERROR", "section": "narrative", "message": "narratives.yaml contains a non-object narrative entry"})
                            continue
                        nid = narrative.get("id", "")
                        if nid in ids:
                            all_issues.append({"level": "ERROR", "section": "narrative", "message": f"Duplicate narrative id '{nid}'"})
                        ids.add(nid)
                        all_issues.extend(validate_narrative(narrative, story_ids))
                    if "getting-started" not in ids:
                        all_issues.append({"level": "ERROR", "section": "narrative", "message": "getting-started narrative is required — teaching-order path covering the main top-level components"})

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
    print(f"\n{'VALID' if valid else 'INVALID'}: {len(errors)} errors, {len(warnings)} warnings")

    if not valid:
        print(f"\nExpected output structure at {analysis_dir}:")
        print(f"  {analysis_dir}/blast.json           — deterministic blast radius JSON")
        print(f"  {analysis_dir}/facts/               — normalized fact domain files")
        print(f"  {analysis_dir}/facts/concept-evidence.json — deterministic concept evidence facts")
        if not DETERMINISTIC_ONLY:
            print(f"  {analysis_dir}/atlas.json           — v4 JSON (see atlas-schema.md)")
            print(f"  {analysis_dir}/stories/*.yaml       — one YAML file per story")
            print(f"  {analysis_dir}/narratives.yaml      — cross-cutting story sequences")

    # Lock management
    if use_lock:
        if valid:
            if lock_path.exists():
                lock_path.unlink()
                print(f"Lock removed: {lock_path}")
        else:
            lock_path.write_text(f"{len(errors)} errors\n")
            print(f"Lock created: {lock_path}")

    sys.exit(0 if valid else 1)


if __name__ == "__main__":
    main()
