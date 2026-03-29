#!/usr/bin/env python3
"""Validate all augur analysis output: atlas.json, stories, journeys, directory structure.

Usage:
    python validate_output.py <project-memory-dir> [--lock]

    <project-memory-dir> is the path containing atlas.json, stories/, journeys/
    e.g., /path/to/project/.kord/agents/augur/memory/

    --lock: create a lock file on failure, remove on success.
            Lock path: <project-memory-dir>/.validate-lock
            A hook can check for this lock to block writes until validation passes.

Checks:
    Phase 1 (atlas):
        - atlas.json exists and is valid JSON
        - Required top-level fields present
        - Version is "3"
        - IDs are kebab-case and unique
        - All cross-references resolve
        - Group count is 3-5
        - Component count is 5-10 (warning if outside 4-12)
        - grounded_in arrays present on flows, state, failure_modes

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
        - overview.yaml exists
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
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None

KEBAB_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")

REQUIRED_ATLAS_FIELDS = [
    "version", "generated", "project", "purpose", "stack",
    "groups", "components", "data_flows", "state",
    "external_dependencies", "failure_modes", "concepts", "debt"
]


def kebab_case(s: str) -> bool:
    return bool(KEBAB_RE.match(s))


def validate_atlas(atlas: dict) -> list[dict]:
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
    if atlas.get("version") != "3":
        error(f"Expected version '3', got '{atlas.get('version')}'", "atlas")

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

    # Data flows
    for f in atlas.get("data_flows", []):
        fid = f.get("id", "")
        if not f.get("grounded_in"):
            warn(f"Flow '{fid}' has no grounded_in", "data_flows")
        for step in f.get("steps", []):
            for key in ("component", "to"):
                ref = step.get(key, "")
                if ref and ref not in all_node_ids:
                    error(f"Flow '{fid}' step {key} references unknown '{ref}'", "data_flows")

    # State
    for s in atlas.get("state", []):
        sid = s.get("id", "")
        if not s.get("grounded_in"):
            warn(f"State '{sid}' has no grounded_in", "state")
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

    # Failure modes
    for fm in atlas.get("failure_modes", []):
        fmid = fm.get("id", "")
        if not fm.get("grounded_in"):
            warn(f"Failure mode '{fmid}' has no grounded_in", "failure_modes")
        for cascade in fm.get("cascade", []):
            ref = cascade.get("component", "")
            if ref and ref not in all_node_ids:
                error(f"Failure mode '{fmid}' cascade references unknown '{ref}'", "failure_modes")

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


def validate_story(story: dict, atlas_node_ids: set) -> list[dict]:
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

    stories = journey.get("stories", [])
    if len(stories) < 3:
        warn(f"Journey '{jid}' has {len(stories)} stories (minimum 3)")
    elif len(stories) > 8:
        warn(f"Journey '{jid}' has {len(stories)} stories (maximum 8)")

    for sid in stories:
        if sid not in story_ids:
            error(f"Journey '{jid}' references unknown story '{sid}'")

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
    use_lock = "--lock" in sys.argv
    lock_path = mem_dir / ".validate-lock"

    if not mem_dir.exists():
        print(f"Directory not found: {mem_dir}")
        sys.exit(2)

    all_issues = []

    # --- Atlas ---
    atlas_path = mem_dir / "atlas.json"
    atlas_node_ids = set()

    if not atlas_path.exists():
        all_issues.append({"level": "ERROR", "section": "structure", "message": "atlas.json not found"})
    elif atlas_path.suffix != ".json":
        all_issues.append({"level": "ERROR", "section": "structure", "message": f"atlas should be .json, got {atlas_path.suffix}"})
    else:
        try:
            atlas = json.loads(atlas_path.read_text())
            issues, atlas_node_ids = validate_atlas(atlas)
            all_issues.extend(issues)
        except json.JSONDecodeError as e:
            all_issues.append({"level": "ERROR", "section": "atlas", "message": f"JSON parse error: {e}"})

    # --- Stories ---
    stories_dir = mem_dir / "stories"
    story_ids = set()

    if not stories_dir.exists():
        all_issues.append({"level": "WARNING", "section": "structure", "message": "stories/ directory not found"})
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
            all_issues.extend(validate_story(story, atlas_node_ids))

    # --- Journeys ---
    journeys_dir = mem_dir / "journeys"

    if not journeys_dir.exists():
        all_issues.append({"level": "WARNING", "section": "structure", "message": "journeys/ directory not found"})
    else:
        has_overview = False
        for f in sorted(journeys_dir.iterdir()):
            if f.suffix not in (".yaml", ".yml"):
                continue
            if f.stem == "overview":
                has_overview = True
            journey = load_yaml(f)
            if journey is None:
                all_issues.append({"level": "ERROR", "section": "journey", "message": f"Failed to parse: {f.name}"})
                continue
            all_issues.extend(validate_journey(journey, story_ids))

        if not has_overview:
            all_issues.append({"level": "ERROR", "section": "journey", "message": "overview.yaml not found (required)"})

    # --- Summary ---
    errors = [i for i in all_issues if i["level"] == "ERROR"]
    warnings = [i for i in all_issues if i["level"] == "WARNING"]

    for i in all_issues:
        section = f" [{i['section']}]" if i.get("section") else ""
        print(f"{i['level']}{section}: {i['message']}")

    valid = len(errors) == 0
    print(f"\n{'VALID' if valid else 'INVALID'}: {len(errors)} errors, {len(warnings)} warnings")

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
