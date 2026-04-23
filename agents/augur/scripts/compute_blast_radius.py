#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
from typing import Any

from analysis_paths import analysis_dir_for_commit, iter_analysis_meta, read_latest_analysis_pointer, write_json


AUGUR_INVALIDATION_PREFIXES = (
    "agents/augur/detectors/",
    "agents/augur/memory/concepts/",
    "agents/augur/memory/indexes/",
    "agents/augur/schemas/",
    "agents/augur/skills/analyze/",
    "agents/augur/bundles/",
    "shared/skills/audit/",
)


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def git_sha(repo_root: Path) -> str:
    result = subprocess.run(
        ["git", "-c", f"safe.directory={repo_root}", "-C", str(repo_root), "rev-parse", "HEAD"],
        check=False,
        capture_output=True,
        text=True,
    )
    return (result.stdout or "").strip() if result.returncode == 0 else ""


def git_commit_time(repo_root: Path, sha: str) -> str:
    result = subprocess.run(
        ["git", "-c", f"safe.directory={repo_root}", "-C", str(repo_root), "show", "-s", "--format=%ct", sha],
        check=False,
        capture_output=True,
        text=True,
    )
    return (result.stdout or "").strip() if result.returncode == 0 else ""


def git_ancestors(repo_root: Path, sha: str) -> list[str]:
    result = subprocess.run(
        ["git", "-c", f"safe.directory={repo_root}", "-C", str(repo_root), "rev-list", sha],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return []
    return [line.strip() for line in (result.stdout or "").splitlines() if line.strip()]


def resolve_previous_analysis(repo_root: Path, project: str, previous_sha: str, current_sha: str, agent_home: str | None = None) -> tuple[str, Path | None, dict[str, Any] | None, str]:
    if previous_sha:
        for analysis_dir, meta in iter_analysis_meta(project, agent_home):
            if str(meta.get("sha") or "") == previous_sha:
                return previous_sha, analysis_dir, meta, "explicit-previous-sha"

    latest = read_latest_analysis_pointer(project, agent_home)
    if isinstance(latest, dict):
        latest_sha = str(latest.get("sha") or "")
        latest_dir_text = str(latest.get("analysis_dir") or "")
        latest_dir = Path(latest_dir_text) if latest_dir_text else None
        if latest_sha and latest_dir and latest_dir.exists():
            if latest_sha == current_sha:
                latest_meta_path = latest_dir / "meta.json"
                latest_meta = read_json(latest_meta_path) if latest_meta_path.exists() else {}
                return latest_sha, latest_dir, latest_meta if isinstance(latest_meta, dict) else None, "latest-pointer-current"
            merge_base = subprocess.run(
                ["git", "-c", f"safe.directory={repo_root}", "-C", str(repo_root), "merge-base", "--is-ancestor", latest_sha, current_sha],
                check=False,
                capture_output=True,
                text=True,
            )
            if merge_base.returncode == 0:
                latest_meta_path = latest_dir / "meta.json"
                latest_meta = read_json(latest_meta_path) if latest_meta_path.exists() else {}
                return latest_sha, latest_dir, latest_meta if isinstance(latest_meta, dict) else None, "latest-pointer"

    ancestors = set(git_ancestors(repo_root, current_sha))
    if current_sha in ancestors:
        ancestors.remove(current_sha)
    for analysis_dir, meta in iter_analysis_meta(project, agent_home):
        analyzed_sha = str(meta.get("sha") or "")
        if analyzed_sha and analyzed_sha in ancestors:
            return analyzed_sha, analysis_dir, meta, "latest-analyzed-ancestor"

    return "", None, None, "no-previous-snapshot"


def git_name_status(repo_root: Path, previous_sha: str, current_sha: str) -> list[dict[str, str]]:
    result = subprocess.run(
        ["git", "-c", f"safe.directory={repo_root}", "-C", str(repo_root), "diff", "--name-status", f"{previous_sha}..{current_sha}"],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return []
    records: list[dict[str, str]] = []
    for raw_line in (result.stdout or "").splitlines():
        line = raw_line.strip()
        if not line:
            continue
        parts = line.split("\t")
        status = parts[0]
        if status.startswith("R") and len(parts) >= 3:
            records.append({
                "status": "R",
                "path": parts[2],
                "old_path": parts[1],
            })
        elif len(parts) >= 2:
            records.append({
                "status": status[:1],
                "path": parts[1],
            })
    return records


def git_diff_stat(repo_root: Path, previous_sha: str, current_sha: str) -> dict[str, Any]:
    result = subprocess.run(
        ["git", "-c", f"safe.directory={repo_root}", "-C", str(repo_root), "diff", "--shortstat", f"{previous_sha}..{current_sha}"],
        check=False,
        capture_output=True,
        text=True,
    )
    text = (result.stdout or "").strip()
    files_changed = 0
    insertions = 0
    deletions = 0
    if text:
        for part in [item.strip() for item in text.split(",")]:
            if "file changed" in part or "files changed" in part:
                files_changed = int(part.split()[0])
            elif "insertion" in part or "insertions" in part:
                insertions = int(part.split()[0])
            elif "deletion" in part or "deletions" in part:
                deletions = int(part.split()[0])
    return {
        "files_changed": files_changed,
        "insertions": insertions,
        "deletions": deletions,
    }


def unique_strings(values: list[str]) -> list[str]:
    seen: dict[str, None] = {}
    for value in values:
        if value and value not in seen:
            seen[value] = None
    return list(seen.keys())


def source_path(value: str) -> str:
    return value.split(":", 1)[0]


def classify_file(path: str) -> str:
    lowered = path.lower()
    name = Path(lowered).name
    if any(lowered.startswith(prefix) for prefix in AUGUR_INVALIDATION_PREFIXES):
        return "augur-input"
    if lowered.startswith(".github/") or lowered.startswith("docs/") or lowered.endswith(".md"):
        return "peripheral"
    if lowered.startswith("test/") or lowered.startswith("tests/") or "/test/" in lowered or "/tests/" in lowered:
        return "peripheral"
    if name in {"package.json", "package-lock.json", "pnpm-lock.yaml", "yarn.lock", "go.mod", "go.sum", "requirements.txt", "pyproject.toml", "pom.xml", "build.gradle", "Cargo.toml"}:
        return "dependency"
    if "migrations/" in lowered or "/schema/" in lowered or name.startswith("schema.") or lowered.endswith(".sql"):
        return "schema"
    return "mapped"


def collect_modules_to_components(atlas: dict[str, Any]) -> dict[str, set[str]]:
    mapping: dict[str, set[str]] = {}
    for component in atlas.get("components") or []:
        if not isinstance(component, dict):
            continue
        component_id = str(component.get("id") or "")
        if not component_id:
            continue
        for module in component.get("modules") or []:
            if not module:
                continue
            mapping.setdefault(str(module), set()).add(component_id)
    return mapping


def collect_dependency_component_map(atlas: dict[str, Any]) -> dict[str, set[str]]:
    mapping: dict[str, set[str]] = {}
    for dependency in atlas.get("external_dependencies") or []:
        if not isinstance(dependency, dict):
            continue
        dependency_id = str(dependency.get("id") or "")
        components = {str(item) for item in dependency.get("components") or [] if item}
        if dependency_id and components:
            mapping[dependency_id] = components
    return mapping


def collect_flow_map(atlas: dict[str, Any]) -> dict[str, dict[str, Any]]:
    flow_map: dict[str, dict[str, Any]] = {}
    for flow in atlas.get("flows") or []:
        if not isinstance(flow, dict):
            continue
        flow_id = str(flow.get("id") or "")
        if flow_id:
            flow_map[flow_id] = flow
    return flow_map


def collect_state_map(atlas: dict[str, Any]) -> dict[str, dict[str, Any]]:
    state_map: dict[str, dict[str, Any]] = {}
    for state in atlas.get("state") or []:
        if not isinstance(state, dict):
            continue
        state_id = str(state.get("id") or "")
        if state_id:
            state_map[state_id] = state
    return state_map


def collect_concepts(atlas: dict[str, Any]) -> list[dict[str, Any]]:
    concepts = atlas.get("concepts") or {}
    detected = concepts.get("detected_patterns") or []
    return [item for item in detected if isinstance(item, dict)]


def map_changed_files_to_components(
    changed: list[dict[str, str]],
    modules_to_components: dict[str, set[str]],
) -> tuple[set[str], list[str]]:
    affected_components: set[str] = set()
    unmapped_files: list[str] = []
    for record in changed:
        path = record["path"]
        category = classify_file(path)
        if category not in {"mapped", "dependency", "schema"}:
            continue
        matched = False
        for module, component_ids in modules_to_components.items():
            if path == module or path.startswith(f"{module.rstrip('/')}/"):
                affected_components.update(component_ids)
                matched = True
        old_path = record.get("old_path") or ""
        if not matched and old_path:
            for module, component_ids in modules_to_components.items():
                if old_path == module or old_path.startswith(f"{module.rstrip('/')}/"):
                    affected_components.update(component_ids)
                    matched = True
        if category == "mapped" and not matched:
            unmapped_files.append(path)
    return affected_components, unmapped_files


def infer_fact_domains(changed: list[dict[str, str]]) -> set[str]:
    affected: set[str] = set()
    for record in changed:
        category = classify_file(record["path"])
        if category == "dependency":
            affected.update({"frameworks", "external-clients", "import-graph", "config"})
        elif category == "schema":
            affected.update({"models", "events"})
        elif category == "mapped":
            affected.update({"routes", "models", "events", "jobs", "external-clients", "import-graph"})
        elif category == "augur-input":
            affected.update({"frameworks", "routes", "models", "events", "jobs", "external-clients", "import-graph", "config"})
    return affected


def main() -> int:
    parser = argparse.ArgumentParser(description="Compute deterministic Augur blast radius between snapshots.")
    parser.add_argument("repo_root", type=Path)
    parser.add_argument("--project", help="Project slug. Defaults to repo dir name.")
    parser.add_argument("--agent-home", help="Agent home directory. Defaults to AGENT_HOME_DIR when set.")
    parser.add_argument("--previous-sha", help="Previous analyzed commit. If missing or unavailable, uses the latest analyzed ancestor.")
    parser.add_argument("--current-sha", help="Current commit. Defaults to HEAD.")
    parser.add_argument("--output", type=Path, help="Write blast-radius manifest to this path.")
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    project = args.project or repo_root.name
    agent_home = args.agent_home
    current_sha = args.current_sha or git_sha(repo_root)
    previous_sha = args.previous_sha or ""

    if not current_sha:
        raise SystemExit("Unable to resolve current git SHA.")

    def emit(payload: dict[str, Any]) -> int:
        if args.output:
            write_json(args.output.resolve(), payload)
        print(json.dumps(payload, indent=2))
        return 0

    current_commit_time = git_commit_time(repo_root, current_sha)
    next_commit_dir = analysis_dir_for_commit(project, current_sha, current_commit_time, agent_home)
    resolved_previous_sha, previous_dir, previous_meta, previous_resolution = resolve_previous_analysis(
        repo_root,
        project,
        previous_sha,
        current_sha,
        agent_home,
    )

    if not resolved_previous_sha or previous_dir is None:
        return emit({
            "project": project,
            "previous_sha": "",
            "previous_commit_time": "",
            "current_sha": current_sha,
            "current_commit_time": current_commit_time,
            "mode": "full",
            "tier": 3,
            "reasons": [previous_resolution],
            "git_diff": {"files_changed": 0, "insertions": 0, "deletions": 0},
            "changed_files": [],
            "changed_entries": [],
            "file_categories": {},
            "affected_components": [],
            "affected_flows": [],
            "affected_state": [],
            "affected_dependencies": [],
            "affected_concepts": [],
            "affected_fact_domains": [],
            "invalidation": {"augur_inputs_changed": False, "paths": []},
            "base_analysis_dir": "",
            "analysis_dir": str(next_commit_dir),
            "previous_resolution": previous_resolution,
        })

    atlas_path = previous_dir / "atlas.json"
    if not atlas_path.exists():
        return emit({
            "project": project,
            "previous_sha": resolved_previous_sha,
            "previous_commit_time": str((previous_meta or {}).get("commit_time") or ""),
            "current_sha": current_sha,
            "current_commit_time": current_commit_time,
            "mode": "full",
            "tier": 3,
            "reasons": ["missing-previous-atlas"],
            "git_diff": {"files_changed": 0, "insertions": 0, "deletions": 0},
            "changed_files": [],
            "changed_entries": [],
            "file_categories": {},
            "affected_components": [],
            "affected_flows": [],
            "affected_state": [],
            "affected_dependencies": [],
            "affected_concepts": [],
            "affected_fact_domains": [],
            "invalidation": {"augur_inputs_changed": False, "paths": []},
            "base_analysis_dir": str(previous_dir),
            "analysis_dir": str(next_commit_dir),
            "previous_resolution": previous_resolution,
        })

    changed_entries = git_name_status(repo_root, resolved_previous_sha, current_sha)
    diff_stat = git_diff_stat(repo_root, resolved_previous_sha, current_sha)
    changed_files = [entry["path"] for entry in changed_entries]

    if not changed_files:
        return emit({
            "project": project,
            "previous_sha": resolved_previous_sha,
            "previous_commit_time": str((previous_meta or {}).get("commit_time") or ""),
            "current_sha": current_sha,
            "current_commit_time": current_commit_time,
            "mode": "skip",
            "tier": 0,
            "reasons": ["no-changed-files"],
            "git_diff": diff_stat,
            "changed_files": [],
            "changed_entries": [],
            "file_categories": {},
            "affected_components": [],
            "affected_flows": [],
            "affected_state": [],
            "affected_dependencies": [],
            "affected_concepts": [],
            "affected_fact_domains": [],
            "invalidation": {"augur_inputs_changed": False, "paths": []},
            "base_analysis_dir": str(previous_dir),
            "analysis_dir": str(next_commit_dir),
            "previous_resolution": previous_resolution,
        })

    atlas = read_json(atlas_path)
    concepts = collect_concepts(atlas)
    modules_to_components = collect_modules_to_components(atlas)
    dependency_map = collect_dependency_component_map(atlas)
    flow_map = collect_flow_map(atlas)
    state_map = collect_state_map(atlas)

    file_categories: dict[str, list[str]] = {}
    for entry in changed_entries:
        file_categories.setdefault(classify_file(entry["path"]), []).append(entry["path"])

    affected_components, unmapped_files = map_changed_files_to_components(changed_entries, modules_to_components)
    affected_fact_domains = infer_fact_domains(changed_entries)
    affected_flows: set[str] = set()
    affected_state: set[str] = set()
    affected_dependencies: set[str] = set()
    affected_concepts: set[str] = set()
    reasons: list[str] = []

    augur_input_changes = sorted(file_categories.get("augur-input", []))

    changed_file_set = set(changed_files)
    rename_old_paths = {entry.get("old_path", "") for entry in changed_entries if entry.get("old_path")}
    deleted_paths = {entry["path"] for entry in changed_entries if entry["status"] == "D"}
    component_set = set(affected_components)

    for flow_id, flow in flow_map.items():
        grounded = {source_path(str(item)) for item in flow.get("grounded_in") or [] if item}
        flow_components = {
            str(step.get("component"))
            for step in flow.get("steps") or []
            if isinstance(step, dict) and step.get("component")
        }
        if grounded & changed_file_set or grounded & rename_old_paths or grounded & deleted_paths or flow_components & component_set:
            affected_flows.add(flow_id)

    for state_id, state in state_map.items():
        grounded = {source_path(str(item)) for item in state.get("grounded_in") or [] if item}
        component = str(state.get("component") or "")
        if grounded & changed_file_set or grounded & rename_old_paths or grounded & deleted_paths or (component and component in component_set):
            affected_state.add(state_id)

    for dependency_id, dependency_components in dependency_map.items():
        if dependency_components & component_set:
            affected_dependencies.add(dependency_id)

    for concept in concepts:
        concept_id = str(concept.get("id") or "")
        components = {str(item) for item in concept.get("components") or [] if item}
        evidence = concept.get("evidence") or {}
        evidence_files = {source_path(str(item)) for item in evidence.get("files") or [] if item}
        evidence_components = {str(item) for item in evidence.get("components") or [] if item}
        if (
            components & component_set
            or evidence_components & component_set
            or evidence_files & changed_file_set
            or evidence_files & rename_old_paths
            or evidence_files & deleted_paths
            or augur_input_changes
        ):
            affected_concepts.add(concept_id)

    component_count = len([item for item in atlas.get("components") or [] if isinstance(item, dict)])
    affected_component_count = len(affected_components)
    total_changed_lines = diff_stat["insertions"] + diff_stat["deletions"]

    if unmapped_files:
        reasons.append("unmapped-files")
    if augur_input_changes:
        reasons.append("augur-inputs-changed")
    if any(entry["status"] == "R" for entry in changed_entries):
        reasons.append("rename-detected")
    if any(entry["status"] == "D" for entry in changed_entries):
        reasons.append("delete-detected")

    if affected_component_count == 0 and set(file_categories).issubset({"peripheral"}):
        mode = "skip"
        tier = 0
        reasons.append("peripheral-only")
    elif augur_input_changes:
        mode = "full"
        tier = 3
    elif unmapped_files or affected_component_count >= max(5, max(component_count // 2, 1)):
        mode = "full"
        tier = 3
        if affected_component_count >= max(5, max(component_count // 2, 1)):
            reasons.append("large-component-blast-radius")
    elif diff_stat["files_changed"] >= 75 or total_changed_lines >= 2000:
        mode = "full"
        tier = 3
        reasons.append("large-diff-stat")
    elif affected_component_count >= 3 or affected_flows or affected_state or affected_concepts:
        mode = "incremental"
        tier = 2 if affected_component_count >= 3 or len(affected_flows) >= 4 else 1
        reasons.append("targeted-rerun")
    else:
        mode = "skip"
        tier = 0
        reasons.append("no-architectural-blast")

    payload = {
        "project": project,
        "previous_sha": resolved_previous_sha,
        "previous_commit_time": str((previous_meta or {}).get("commit_time") or ""),
        "current_sha": current_sha,
        "current_commit_time": current_commit_time,
        "mode": mode,
        "tier": tier,
        "reasons": unique_strings(reasons),
        "git_diff": diff_stat,
        "changed_files": changed_files,
        "changed_entries": changed_entries,
        "file_categories": {key: value for key, value in sorted(file_categories.items())},
        "affected_components": sorted(affected_components),
        "affected_flows": sorted(affected_flows),
        "affected_state": sorted(affected_state),
        "affected_dependencies": sorted(affected_dependencies),
        "affected_concepts": sorted(affected_concepts),
        "affected_fact_domains": sorted(affected_fact_domains),
        "invalidation": {
            "augur_inputs_changed": bool(augur_input_changes),
            "paths": augur_input_changes,
        },
        "base_analysis_dir": str(previous_dir),
        "analysis_dir": str(next_commit_dir),
        "previous_resolution": previous_resolution,
    }

    return emit(payload)


if __name__ == "__main__":
    raise SystemExit(main())
