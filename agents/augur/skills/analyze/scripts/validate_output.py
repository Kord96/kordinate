#!/usr/bin/env python3
"""Validate Augur analysis output for deterministic and semantic phases.

Usage:
    python validate_output.py <analysis-dir>

    <analysis-dir> is the validated Augur analysis directory.
    Deterministic-only runs must contain blast.json, facts/, and facts/concept-evidence.json.
    Full semantic runs must also contain atlas.json, stories/, and narratives.yaml.
    e.g., /kord/augur/memory/projects/<project>/analysis/<commit-time>-<sha>/

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
        - Group count is 3-5
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
        - getting-started narrative exists
        - Each narrative references existing story IDs
        - Narrative length is 3-8 stories

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
    "version", "generated", "project", "purpose", "stack",
    "groups", "components", "flows", "state",
    "external_dependencies", "concepts", "debt"
]

DETERMINISTIC_ONLY = (
    os.getenv("AUGUR_DETERMINISTIC_ONLY") in ("1", "true", "TRUE", "yes", "YES")
)


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


def validate_health(
    health: dict | None,
    section: str,
    item_id: str,
    project_root: Path | None = None,
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
        elif project_root:
            issues.extend(check_grounded_in(grounded, project_root, section, f"{item_id}/{failure_id}"))
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
            issues.extend(validate_health(c.get("health"), "components", cid or "<component>", project_root))
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

    # Flows
    for f in atlas.get("flows", []):
        fid = f.get("id", "")
        if not f.get("grounded_in"):
            warn(f"Flow '{fid}' has no grounded_in", "flows")
        elif project_root:
            issues.extend(check_grounded_in(f["grounded_in"], project_root, "flows", fid))
        issues.extend(validate_health(f.get("health"), "flows", fid or "<flow>", project_root))
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
            elif project_root:
                issues.extend(check_grounded_in(grounded, project_root, "flows", f"{fid}/{metric.get('name', '?')}"))
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

    # External dependency health
    for dependency in atlas.get("external_dependencies", []):
        did = dependency.get("id", "")
        issues.extend(validate_health(dependency.get("health"), "external_dependencies", did or "<dependency>", project_root))

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
        elif project_root:
            issues.extend(check_grounded_in(obs["grounded_in"], project_root, "story", f"{sid}/{oid}"))
        comp = obs.get("component", "")
        if comp and comp not in atlas_node_ids:
            error(f"Story '{sid}' observation component '{comp}' not in atlas")

    return issues


def validate_narrative(narrative: dict, story_ids: set) -> list[dict]:
    issues = []

    def error(msg):
        issues.append({"level": "ERROR", "section": "journey", "message": msg})

    def warn(msg):
        issues.append({"level": "WARNING", "section": "journey", "message": msg})

    jid = narrative.get("id", "<unknown>")

    if "id" not in narrative:
        error("Narrative missing required field: id")
    if "title" not in narrative:
        error(f"Narrative '{jid}' missing required field: title")

    stories = narrative.get("stories", [])
    if len(stories) < 3:
        warn(f"Narrative '{jid}' has {len(stories)} stories (minimum 3)")
    elif len(stories) > 8:
        warn(f"Narrative '{jid}' has {len(stories)} stories (maximum 8)")

    for entry in stories:
        if isinstance(entry, dict):
            sid = entry.get("id", "")
        else:
            sid = entry
        if sid not in story_ids:
            error(f"Narrative '{jid}' references unknown story '{sid}'")

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
    # Project code lives at /kord/shared/repos/<project>/
    project_root = None
    if "projects" in analysis_dir.parts:
        proj_idx = analysis_dir.parts.index("projects")
        if proj_idx + 1 < len(analysis_dir.parts):
            project_name = analysis_dir.parts[proj_idx + 1]
            for candidate in (
                Path("/kord/repos") / project_name,
                Path("/kord/shared/repos") / project_name,
                Path("/kord/projects") / project_name,
            ):
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
    if not concepts_path.exists():
        all_issues.append({"level": "ERROR", "section": "structure", "message": f"facts/concept-evidence.json not found at {concepts_path}. Write deterministic concept evidence facts to this exact path."})
    else:
        try:
            json.loads(concepts_path.read_text())
        except json.JSONDecodeError as e:
            all_issues.append({"level": "ERROR", "section": "concept-evidence", "message": f"JSON parse error: {e}"})

    atlas_node_ids = set()
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
                issues, atlas_node_ids = validate_atlas(atlas, project_root)
                all_issues.extend(issues)
            except json.JSONDecodeError as e:
                all_issues.append({"level": "ERROR", "section": "atlas", "message": f"JSON parse error: {e}"})

    story_ids = set()
    if not DETERMINISTIC_ONLY:
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

        # --- Narratives ---
        narratives_path = analysis_dir / "narratives.yaml"
        if not narratives_path.exists():
            all_issues.append({"level": "ERROR", "section": "structure", "message": f"narratives.yaml not found at {narratives_path}. Write cross-cutting story sequences here."})
        else:
            narratives_doc = load_yaml(narratives_path)
            if narratives_doc is None:
                all_issues.append({"level": "ERROR", "section": "narrative", "message": f"Failed to parse: {narratives_path.name}"})
            else:
                narratives = narratives_doc.get("narratives", []) if isinstance(narratives_doc, dict) else []
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
                        all_issues.append({"level": "ERROR", "section": "narrative", "message": "getting-started narrative is required — teaching-order path covering all groups"})

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
