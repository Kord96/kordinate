#!/usr/bin/env python3
"""Validate atlas.json against the v3 schema.

Usage:
    python validate_atlas.py <path-to-atlas.json> [--strict]

Checks:
    - Required top-level fields present
    - IDs are kebab-case and unique within sections
    - All cross-references resolve
    - Group count is 3-5
    - Component count is 5-10 (warning if outside 4-12)
    - grounded_in arrays are present and non-empty on flows, state, failure_modes
    - No orphaned references

Exit codes:
    0 = valid
    1 = errors found
    2 = file not found or parse error
"""

import json
import re
import sys
from pathlib import Path

KEBAB_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")

REQUIRED_TOP_LEVEL = [
    "version", "generated", "project", "purpose", "stack",
    "groups", "components", "data_flows", "state",
    "external_dependencies", "failure_modes", "concepts", "debt"
]


def kebab_case(s: str) -> bool:
    return bool(KEBAB_RE.match(s))


def validate(atlas: dict, strict: bool = False) -> list[dict]:
    issues = []

    def error(msg, section=""):
        issues.append({"level": "ERROR", "section": section, "message": msg})

    def warn(msg, section=""):
        issues.append({"level": "WARNING", "section": section, "message": msg})

    def info(msg, section=""):
        issues.append({"level": "INFO", "section": section, "message": msg})

    # --- Required fields ---
    for field in REQUIRED_TOP_LEVEL:
        if field not in atlas:
            error(f"Missing required field: {field}", "top-level")

    # --- Version ---
    if atlas.get("version") != "3":
        error(f"Expected version '3', got '{atlas.get('version')}'", "version")

    # --- Groups ---
    groups = atlas.get("groups", [])
    if len(groups) < 3:
        error(f"Too few groups: {len(groups)} (minimum 3)", "groups")
    elif len(groups) > 5:
        error(f"Too many groups: {len(groups)} (maximum 5)", "groups")

    group_ids = {g.get("id") for g in groups}
    for g in groups:
        gid = g.get("id", "")
        if not kebab_case(gid):
            error(f"Group ID not kebab-case: '{gid}'", "groups")

    # --- Components ---
    components = atlas.get("components", [])
    if len(components) < 4:
        warn(f"Few components: {len(components)} (expected 5-10)", "components")
    elif len(components) > 12:
        warn(f"Many components: {len(components)} (expected 5-10)", "components")

    component_ids = set()
    for c in components:
        cid = c.get("id", "")
        if not kebab_case(cid):
            error(f"Component ID not kebab-case: '{cid}'", "components")
        if cid in component_ids:
            error(f"Duplicate component ID: '{cid}'", "components")
        component_ids.add(cid)

        # Group reference
        cgroup = c.get("group", "")
        if cgroup and cgroup not in group_ids:
            error(f"Component '{cid}' references unknown group '{cgroup}'", "components")

        # depends_on references
        for dep in c.get("depends_on", []):
            if dep not in component_ids and dep != cid:
                # defer check — might be forward reference
                pass

        # Collect children recursively
        def collect_children(node):
            for child in node.get("children", []):
                child_id = child.get("id", "")
                if child_id:
                    component_ids.add(child_id)
                collect_children(child)
        collect_children(c)

    # Second pass for depends_on after all IDs collected
    for c in components:
        for dep in c.get("depends_on", []):
            if dep not in component_ids:
                error(f"Component '{c.get('id')}' depends_on unknown '{dep}'", "components")

    # --- All known node IDs (components + actors + external deps + state) ---
    actor_ids = {a.get("id") for a in atlas.get("actors", [])}
    ext_dep_ids = {e.get("id") for e in atlas.get("external_dependencies", [])}
    state_ids = {s.get("id") for s in atlas.get("state", [])}
    all_node_ids = component_ids | actor_ids | ext_dep_ids | state_ids

    # --- Data flows ---
    flows = atlas.get("data_flows", [])
    flow_ids = set()
    for f in flows:
        fid = f.get("id", "")
        if fid in flow_ids:
            error(f"Duplicate flow ID: '{fid}'", "data_flows")
        flow_ids.add(fid)

        if not f.get("grounded_in"):
            warn(f"Flow '{fid}' has no grounded_in references", "data_flows")

        for step in f.get("steps", []):
            comp = step.get("component", "")
            if comp and comp not in all_node_ids:
                error(f"Flow '{fid}' step references unknown component '{comp}'", "data_flows")
            to = step.get("to", "")
            if to and to not in all_node_ids:
                error(f"Flow '{fid}' step 'to' references unknown component '{to}'", "data_flows")

    # --- State ---
    for s in atlas.get("state", []):
        sid = s.get("id", "")
        if not s.get("grounded_in"):
            warn(f"State '{sid}' has no grounded_in references", "state")
        comp = s.get("component", "")
        if comp and comp not in all_node_ids:
            error(f"State '{sid}' references unknown component '{comp}'", "state")
        for r in s.get("readers", []):
            if r not in all_node_ids:
                error(f"State '{sid}' reader references unknown '{r}'", "state")
        for w in s.get("writers", []):
            if w not in all_node_ids:
                error(f"State '{sid}' writer references unknown '{w}'", "state")

    # --- Failure modes ---
    for fm in atlas.get("failure_modes", []):
        fmid = fm.get("id", "")
        if not fm.get("grounded_in"):
            warn(f"Failure mode '{fmid}' has no grounded_in references", "failure_modes")
        for cascade in fm.get("cascade", []):
            comp = cascade.get("component", "")
            if comp and comp not in all_node_ids:
                error(f"Failure mode '{fmid}' cascade references unknown '{comp}'", "failure_modes")

    # --- Concepts ---
    concepts = atlas.get("concepts", {})
    for p in concepts.get("detected_patterns", []):
        for comp in p.get("components", []):
            if comp not in all_node_ids:
                error(f"Pattern '{p.get('id')}' references unknown component '{comp}'", "concepts")
    for ap in concepts.get("detected_anti_patterns", []):
        for comp in ap.get("components", []):
            if comp not in all_node_ids:
                error(f"Anti-pattern '{ap.get('id')}' references unknown component '{comp}'", "concepts")

    # --- Debt ---
    debt = atlas.get("debt", {})
    for v in debt.get("violations", []):
        for comp in v.get("components", []):
            if comp not in all_node_ids:
                error(f"Debt violation references unknown component '{comp}'", "debt")

    # --- API surface ---
    api = atlas.get("api_surface", {})
    # No cross-ref checks needed — endpoints reference files, not node IDs

    # --- Summary ---
    errors = [i for i in issues if i["level"] == "ERROR"]
    warnings = [i for i in issues if i["level"] == "WARNING"]
    infos = [i for i in issues if i["level"] == "INFO"]

    return issues


def validate_story(story: dict, atlas_node_ids: set) -> list[dict]:
    """Validate a story YAML file against the story schema."""
    issues = []

    def error(msg):
        issues.append({"level": "ERROR", "message": msg})

    def warn(msg):
        issues.append({"level": "WARNING", "message": msg})

    if "id" not in story:
        error("Missing required field: id")
    if "title" not in story:
        error("Missing required field: title")
    if "summary" not in story:
        error("Missing required field: summary")

    # Check bold refs in summary
    summary = story.get("summary", "")
    bold_refs = re.findall(r"\*\*([^*]+)\*\*", summary)
    for ref in bold_refs:
        ref_kebab = ref.lower().replace(" ", "-")
        if ref_kebab not in atlas_node_ids and ref not in atlas_node_ids:
            error(f"Bold ref '**{ref}**' in summary doesn't match any atlas node ID")

    # Check word count
    word_count = len(summary.split())
    if word_count > 100:
        warn(f"Summary is {word_count} words (target: 50-80, max: 100)")

    # Check structure node references
    for struct in story.get("structures", []):
        for node in struct.get("nodes", []):
            nid = node.get("id", "") if isinstance(node, dict) else node
            if nid not in atlas_node_ids:
                error(f"Structure node '{nid}' not in atlas")

    # Check flow node references
    for flow in story.get("flows", []):
        for step in flow.get("steps", []):
            node = step.get("node", "")
            if node and node not in atlas_node_ids:
                error(f"Flow step references unknown node '{node}'")
            to = step.get("to", "")
            if to and to not in atlas_node_ids:
                error(f"Flow step 'to' references unknown node '{to}'")

    # Check observation grounded_in
    for obs in story.get("observations", []):
        if not obs.get("grounded_in"):
            warn(f"Observation '{obs.get('id', '?')}' has no grounded_in references")
        comp = obs.get("component", "")
        if comp and comp not in atlas_node_ids:
            error(f"Observation component '{comp}' not in atlas")

    return issues


def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <atlas.json> [--strict]")
        sys.exit(2)

    path = Path(sys.argv[1])
    strict = "--strict" in sys.argv

    if not path.exists():
        print(f"File not found: {path}")
        sys.exit(2)

    try:
        atlas = json.loads(path.read_text())
    except json.JSONDecodeError as e:
        print(f"JSON parse error: {e}")
        sys.exit(2)

    issues = validate(atlas, strict)

    errors = [i for i in issues if i["level"] == "ERROR"]
    warnings = [i for i in issues if i["level"] == "WARNING"]

    if issues:
        for i in issues:
            section = f" [{i['section']}]" if i.get("section") else ""
            print(f"{i['level']}{section}: {i['message']}")

    print(f"\n{'VALID' if not errors else 'INVALID'}: {len(errors)} errors, {len(warnings)} warnings")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
