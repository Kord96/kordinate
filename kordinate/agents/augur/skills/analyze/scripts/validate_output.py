#!/usr/bin/env python3
"""Validate all augur analysis output: atlas.json, stories, journeys, directory structure.

Usage:
    python validate_output.py <project-memory-dir>

    <project-memory-dir> is the path containing atlas.json, stories/, journeys/
    e.g., /path/to/project/.kord/agents/augur/memory/

Lock management is automatic when VALIDATE_LOCK=1 is set in the environment.
This is used by the hook infrastructure, not by the agent directly.

Checks:
    Phase 1 (atlas):
        - atlas.json exists and is valid JSON
        - Required top-level fields present
        - Version is "4"
        - IDs are kebab-case and unique
        - All cross-references resolve
        - Group count is 3-5
        - Component count is 5-10 (warning if outside 4-12)
        - Flow type is one of: data, control, event, state, resource
        - grounded_in arrays present on flows, state, failure_modes
        - Bounded contexts reference valid modules
        - State entries have schema_evolution and concurrency
        - Observability, security, developer_experience grounded_in valid
        - CI/CD and IaC entries in module_graph

    Phase 2 (stories):
        - stories/ directory exists
        - Each file is valid YAML
        - Required fields: id, title, summary
        - Summary word count <= 100
        - Bold refs in summary resolve to atlas node IDs
        - Structure/flow node refs resolve to atlas
        - Observations have grounded_in

    Phase 2 (journeys):
        - journeys/ directory exists
        - getting-started.yaml exists
        - Each journey references existing story IDs
        - Journey length is 3-8 stories

    Structure:
        - atlas.json is JSON (not YAML)
        - stories/*.yaml are YAML (not .md or .json)
        - journeys/*.yaml are YAML

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

VALID_FLOW_TYPES = {"data", "control", "event", "state", "resource"}

REQUIRED_ATLAS_FIELDS = [
    "version", "generated", "project", "purpose", "stack",
    "groups", "components", "flows", "state",
    "external_dependencies", "failure_modes", "concepts", "debt"
]


def kebab_case(s: str) -> bool:
    return bool(KEBAB_RE.match(s))


def check_grounded_in(refs: list, project_root: Path | None, section: str, item_id: str) -> list[dict]:
    """Verify grounded_in file:line references point to real files."""
    issues = []
    if not project_root:
        return issues
    for ref in refs:
        filepath = ref.split(":")[0]
        full_path = project_root / filepath
        if not full_path.exists():
            issues.append({"level": "ERROR", "section": section,
                           "message": f"'{item_id}' grounded_in references non-existent file: {filepath}"})
    return issues


def validate_atlas(atlas: dict, project_root: Path | None = None) -> list[dict]:
    issues = []

    def error(msg, section=""):
        issues.append({"level": "ERROR", "section": section, "message": msg})

    def warn(msg, section=""):
        issues.append({"level": "WARNING", "section": section, "message": msg})

    # Required fields
    for field in REQUIRED_ATLAS_FIELDS:
        if field not in atlas:
            error(f"Missing required field: {field}", "atlas")

    # Version
    if atlas.get("version") != "4":
        error(f"Expected version '4', got '{atlas.get('version')}'", "atlas")

    # Groups
    groups = atlas.get("groups", [])
    if len(groups) < 3:
        error(f"Too few groups: {len(groups)} (minimum 3)", "groups")
    elif len(groups) > 5:
        error(f"Too many groups: {len(groups)} (maximum 5)", "groups")

    group_ids = set()
    for g in groups:
        gid = g.get("id", "")
        if not kebab_case(gid):
            error(f"Group ID not kebab-case: '{gid}'", "groups")
        if gid in group_ids:
            error(f"Duplicate group ID: '{gid}'", "groups")
        group_ids.add(gid)
        # Per-group component count (2-5 rule)
        group_comps = g.get("components", [])
        if len(group_comps) > 5:
            error(f"Group '{gid}' has {len(group_comps)} components (max 5). Split the group or consolidate components.", "groups")
        elif len(group_comps) < 2:
            warn(f"Group '{gid}' has {len(group_comps)} component (min 2). Merge with another group.", "groups")

    # Components
    components = atlas.get("components", [])
    if len(components) < 4:
        warn(f"Few components: {len(components)} (expected 5-10)", "components")
    elif len(components) > 12:
        warn(f"Many components: {len(components)} (expected 5-10)", "components")

    component_ids = set()

    def collect_component_ids(comps):
        for c in comps:
            cid = c.get("id", "")
            if cid:
                if not kebab_case(cid):
                    error(f"Component ID not kebab-case: '{cid}'", "components")
                if cid in component_ids:
                    error(f"Duplicate component ID: '{cid}'", "components")
                component_ids.add(cid)
            cgroup = c.get("group", "")
            if cgroup and cgroup not in group_ids:
                error(f"Component '{cid}' references unknown group '{cgroup}'", "components")
            collect_component_ids(c.get("children", []))

    collect_component_ids(components)

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
            check_deps(c.get("children", []))

    check_deps(components)

    # Flows (typed)
    for f in atlas.get("flows", []):
        fid = f.get("id", "")
        ftype = f.get("type", "")
        if ftype not in VALID_FLOW_TYPES:
            error(f"Flow '{fid}' has invalid type '{ftype}' (must be one of: {', '.join(sorted(VALID_FLOW_TYPES))})", "flows")
        if not f.get("grounded_in"):
            warn(f"Flow '{fid}' has no grounded_in", "flows")
        elif project_root:
            issues.extend(check_grounded_in(f["grounded_in"], project_root, "flows", fid))
        for step in f.get("steps", []):
            for key in ("component", "to"):
                ref = step.get(key, "")
                if ref and ref not in all_node_ids:
                    error(f"Flow '{fid}' step {key} references unknown '{ref}'", "flows")

    # Legacy data_flows check
    if "data_flows" in atlas:
        error("Found 'data_flows' — v4 uses 'flows' with type discriminator. Migrate data_flows entries to flows with type: 'data'", "atlas")

    # State
    for s in atlas.get("state", []):
        sid = s.get("id", "")
        if not s.get("grounded_in"):
            warn(f"State '{sid}' has no grounded_in", "state")
        elif project_root:
            issues.extend(check_grounded_in(s["grounded_in"], project_root, "state", sid))
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
        # v4: schema_evolution and concurrency
        if not s.get("schema_evolution"):
            warn(f"State '{sid}' missing schema_evolution", "state")
        if not s.get("concurrency"):
            warn(f"State '{sid}' missing concurrency", "state")

    # Bounded contexts
    domain_model = atlas.get("domain_model", {})
    for bc in domain_model.get("bounded_contexts", []):
        bcid = bc.get("id", "")
        if not kebab_case(bcid):
            error(f"Bounded context ID not kebab-case: '{bcid}'", "domain_model")

    # Failure modes
    for fm in atlas.get("failure_modes", []):
        fmid = fm.get("id", "")
        if not fm.get("grounded_in"):
            warn(f"Failure mode '{fmid}' has no grounded_in", "failure_modes")
        elif project_root:
            issues.extend(check_grounded_in(fm["grounded_in"], project_root, "failure_modes", fmid))
        for cascade in fm.get("cascade", []):
            ref = cascade.get("component", "")
            if ref and ref not in all_node_ids:
                error(f"Failure mode '{fmid}' cascade references unknown '{ref}'", "failure_modes")

    # Observability
    obs = atlas.get("observability", {})
    if obs:
        for sub in ("logging", "metrics", "tracing"):
            sub_section = obs.get(sub, {})
            if sub_section and sub_section.get("grounded_in") and project_root:
                issues.extend(check_grounded_in(sub_section["grounded_in"], project_root, "observability", sub))

    # Security
    sec = atlas.get("security", {})
    if sec:
        for sub in ("authentication", "authorization", "secrets_management"):
            sub_section = sec.get(sub, {})
            if sub_section and sub_section.get("grounded_in") and project_root:
                issues.extend(check_grounded_in(sub_section["grounded_in"], project_root, "security", sub))
        # Check for hardcoded secrets
        secrets = sec.get("secrets_management", {})
        if secrets.get("strategy") == "hardcoded":
            error("Secrets management strategy is 'hardcoded' — this should be flagged as critical debt", "security")

    # Developer experience
    devex = atlas.get("developer_experience", {})
    if devex:
        testing = devex.get("testing", {})
        if testing and testing.get("grounded_in") and project_root:
            issues.extend(check_grounded_in(testing["grounded_in"], project_root, "developer_experience", "testing"))

    # Module graph: CI/CD and IaC
    module_graph = atlas.get("module_graph", {})
    for ci in module_graph.get("ci_cd", []):
        ci_file = ci.get("file", "")
        if ci_file and project_root:
            full = project_root / ci_file
            if not full.exists():
                warn(f"CI/CD entry references non-existent file: {ci_file}", "module_graph")
    for iac_entry in module_graph.get("iac", []):
        for iac_file in iac_entry.get("files", []):
            if iac_file and project_root:
                full = project_root / iac_file
                if not full.exists():
                    warn(f"IaC entry references non-existent file: {iac_file}", "module_graph")

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

    # Debt
    for v in atlas.get("debt", {}).get("violations", []):
        for comp in v.get("components", []):
            if comp not in all_node_ids:
                error(f"Debt violation references unknown component '{comp}'", "debt")

    return issues, all_node_ids


def validate_story(story: dict, atlas_node_ids: set, project_root: Path | None = None) -> list[dict]:
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
    if "summary" not in story:
        error(f"Story '{sid}' missing required field: summary")

    # Summary word count
    summary = story.get("summary", "")
    word_count = len(summary.split())
    if word_count > 100:
        warn(f"Story '{sid}' summary is {word_count} words (max 100)")

    # Bold refs in summary
    bold_refs = re.findall(r"\*\*([^*]+)\*\*", summary)
    for ref in bold_refs:
        ref_kebab = ref.lower().replace(" ", "-")
        if ref_kebab not in atlas_node_ids and ref not in atlas_node_ids:
            error(f"Story '{sid}' bold ref '**{ref}**' doesn't match any atlas node")

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

    # Flow node refs and type validation
    for flow in story.get("flows", []):
        ftype = flow.get("type", "")
        if ftype and ftype not in VALID_FLOW_TYPES:
            warn(f"Story '{sid}' flow '{flow.get('id', '?')}' has non-standard type '{ftype}'")
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
        elif project_root:
            issues.extend(check_grounded_in(obs["grounded_in"], project_root, "story", f"{sid}/{oid}"))
        comp = obs.get("component", "")
        if comp and comp not in atlas_node_ids:
            error(f"Story '{sid}' observation component '{comp}' not in atlas")

    return issues


def validate_journey(journey: dict, story_ids: set) -> list[dict]:
    issues = []

    def error(msg):
        issues.append({"level": "ERROR", "section": "journey", "message": msg})

    def warn(msg):
        issues.append({"level": "WARNING", "section": "journey", "message": msg})

    jid = journey.get("id", "<unknown>")

    if "id" not in journey:
        error("Journey missing required field: id")
    if "title" not in journey:
        error(f"Journey '{jid}' missing required field: title")
    if "number" not in journey:
        warn(f"Journey '{jid}' missing field: number (getting-started should be 1)")
    if not journey.get("overview"):
        warn(f"Journey '{jid}' missing overview (2-3 sentence framing for the audience)")

    stories = journey.get("stories", [])
    if len(stories) < 3:
        warn(f"Journey '{jid}' has {len(stories)} stories (minimum 3)")
    elif len(stories) > 8:
        warn(f"Journey '{jid}' has {len(stories)} stories (maximum 8)")

    for sid in stories:
        if sid not in story_ids:
            error(f"Journey '{jid}' references unknown story '{sid}'")

    # Bridge validation
    bridges = journey.get("bridges", [])
    is_getting_started = jid == "getting-started"

    if is_getting_started and len(stories) > 1 and len(bridges) != len(stories) - 1:
        error(f"Journey '{jid}' needs {len(stories) - 1} bridges for {len(stories)} stories (has {len(bridges)}). Add bridges connecting each adjacent pair.")

    for bridge in bridges:
        if not isinstance(bridge, dict):
            error(f"Journey '{jid}' bridge must be an object with from/to/text, got: {type(bridge).__name__}")
            continue
        bfrom = bridge.get("from", "")
        bto = bridge.get("to", "")
        if bfrom and bfrom not in stories:
            error(f"Journey '{jid}' bridge from '{bfrom}' not in stories list")
        if bto and bto not in stories:
            error(f"Journey '{jid}' bridge to '{bto}' not in stories list")
        if bfrom and bto and bfrom in stories and bto in stories:
            fi = stories.index(bfrom)
            ti = stories.index(bto)
            if ti != fi + 1:
                error(f"Journey '{jid}' bridge from '{bfrom}' to '{bto}' — not adjacent in stories order")
        if not bridge.get("text"):
            error(f"Journey '{jid}' bridge from '{bfrom}' to '{bto}' has no text")

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
        print(f"Usage: {sys.argv[0]} <project-memory-dir> [--lock]")
        sys.exit(2)

    mem_dir = Path(sys.argv[1])
    use_lock = os.environ.get("VALIDATE_LOCK") == "1"
    lock_path = mem_dir / ".validate-lock"

    if not mem_dir.exists():
        print(f"Directory not found: {mem_dir}")
        sys.exit(2)

    all_issues = []

    # Derive project root from memory dir path
    # Expected: <project>/.kord/agents/augur/memory/ → project root is 4 levels up
    project_root = None
    if ".kord" in mem_dir.parts:
        kord_idx = mem_dir.parts.index(".kord")
        project_root = Path(*mem_dir.parts[:kord_idx])
        if not project_root.exists():
            project_root = None

    # --- Atlas ---
    atlas_path = mem_dir / "atlas.json"
    atlas_node_ids = set()

    if not atlas_path.exists():
        all_issues.append({"level": "ERROR", "section": "structure", "message": f"atlas.json not found at {atlas_path}. Write your atlas to this exact path."})
    elif atlas_path.suffix != ".json":
        all_issues.append({"level": "ERROR", "section": "structure", "message": f"atlas should be .json, got {atlas_path.suffix}"})
    else:
        try:
            atlas = json.loads(atlas_path.read_text())
            issues, atlas_node_ids = validate_atlas(atlas, project_root)
            all_issues.extend(issues)
        except json.JSONDecodeError as e:
            all_issues.append({"level": "ERROR", "section": "atlas", "message": f"JSON parse error: {e}"})

    # --- Stories ---
    stories_dir = mem_dir / "stories"
    story_ids = set()

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
            all_issues.extend(validate_story(story, atlas_node_ids, project_root))

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

    # --- Journeys ---
    journeys_dir = mem_dir / "journeys"

    if not journeys_dir.exists():
        all_issues.append({"level": "ERROR", "section": "structure", "message": f"journeys/ directory not found at {journeys_dir}. Write at least getting-started.yaml here."})
    else:
        for f in sorted(journeys_dir.iterdir()):
            if f.suffix not in (".yaml", ".yml"):
                continue
            journey = load_yaml(f)
            if journey is None:
                all_issues.append({"level": "ERROR", "section": "journey", "message": f"Failed to parse: {f.name}"})
                continue
            all_issues.extend(validate_journey(journey, story_ids))

        journey_count = sum(1 for f in journeys_dir.iterdir() if f.suffix in (".yaml", ".yml"))
        has_getting_started = any(f.stem == "getting-started" for f in journeys_dir.iterdir() if f.suffix in (".yaml", ".yml"))
        if not has_getting_started:
            all_issues.append({"level": "ERROR", "section": "journey", "message": "getting-started.yaml is required — teaching-order journey covering all groups"})
        if journey_count < 3:
            all_issues.append({"level": "ERROR", "section": "journey", "message": f"Need at least 3 journeys (have {journey_count}). Every project has at least 3 distinct perspectives."})

    # --- Summary ---
    errors = [i for i in all_issues if i["level"] == "ERROR"]
    warnings = [i for i in all_issues if i["level"] == "WARNING"]

    for i in all_issues:
        section = f" [{i['section']}]" if i.get("section") else ""
        print(f"{i['level']}{section}: {i['message']}")

    valid = len(errors) == 0
    print(f"\n{'VALID' if valid else 'INVALID'}: {len(errors)} errors, {len(warnings)} warnings")

    if not valid:
        print(f"\nExpected output structure at {mem_dir}:")
        print(f"  {mem_dir}/atlas.json          — v4 JSON (see atlas-schema.md)")
        print(f"  {mem_dir}/stories/*.yaml       — one YAML file per story")
        print(f"  {mem_dir}/journeys/*.yaml      — at least getting-started.yaml")

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
