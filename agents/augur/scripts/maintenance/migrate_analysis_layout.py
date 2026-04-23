#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path
from typing import Any

LIB_DIR = Path(__file__).resolve().parents[1] / "lib"
if str(LIB_DIR) not in sys.path:
    sys.path.insert(0, str(LIB_DIR))

from analysis_paths import (
    ANALYSIS_ID_RE,
    LEGACY_ANALYSIS_ID_RE,
    normalize_sha_key,
    project_analysis_dir,
    write_analysis_indexes,
)


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def ensure_overlay_and_reflection_indexes(run_dir: Path, analysis_id: str) -> None:
    overlays_dir = run_dir / "overlays"
    reflections_dir = run_dir / "reflections"
    overlays_dir.mkdir(parents=True, exist_ok=True)
    reflections_dir.mkdir(parents=True, exist_ok=True)
    overlays_index = overlays_dir / "index.json"
    reflections_index = reflections_dir / "index.json"
    if not overlays_index.exists():
        write_json(overlays_index, {"analysis_id": analysis_id, "overlays": []})
    if not reflections_index.exists():
        write_json(reflections_index, {"analysis_id": analysis_id, "reflections": []})


def rewrite_meta_paths(run_dir: Path, meta: dict[str, Any]) -> None:
    artifacts = meta.setdefault("artifacts", {})
    if isinstance(artifacts, dict):
        artifacts["root"] = str(run_dir)
        artifacts["atlas"] = str(run_dir / "atlas.json") if (run_dir / "atlas.json").exists() else ""
        artifacts["startup"] = str(run_dir / "startup.json") if (run_dir / "startup.json").exists() else ""
        artifacts["index"] = str(run_dir / "index.json") if (run_dir / "index.json").exists() else ""
        artifacts.pop("facts_index", None)
        artifacts["stories_dir"] = str(run_dir / "stories") if (run_dir / "stories").exists() else ""
        artifacts["narratives"] = str(run_dir / "narratives.yaml") if (run_dir / "narratives.yaml").exists() else ""
        artifacts["blast"] = str(run_dir / "blast.json") if (run_dir / "blast.json").exists() else ""
        artifacts["overlays_dir"] = str(run_dir / "overlays")
        artifacts["overlays_index"] = str(run_dir / "overlays" / "index.json")
        artifacts["reflections_dir"] = str(run_dir / "reflections")
        artifacts["reflections_index"] = str(run_dir / "reflections" / "index.json")


def is_legacy_run_dir(path: Path) -> bool:
    return path.is_dir() and (ANALYSIS_ID_RE.match(path.name) or LEGACY_ANALYSIS_ID_RE.match(path.name))


def migrate_project(project: str, agent_home: Path, dry_run: bool = False) -> list[dict[str, str]]:
    analysis_root = project_analysis_dir(project, agent_home)
    if not analysis_root.exists():
        return []

    operations: list[dict[str, str]] = []
    for candidate in sorted(analysis_root.iterdir(), key=lambda p: p.name):
        if not is_legacy_run_dir(candidate):
            continue
        meta_path = candidate / "meta.json"
        if not meta_path.exists():
            continue
        meta = read_json(meta_path)
        sha = normalize_sha_key(str(meta.get("sha") or ""))
        target = analysis_root / sha / candidate.name
        if target == candidate:
            continue
        if target.exists():
            operations.append({
                "project": project,
                "run_dir": str(candidate),
                "target_dir": str(target),
                "status": "skipped-target-exists",
            })
            continue

        operations.append({
            "project": project,
            "run_dir": str(candidate),
            "target_dir": str(target),
            "status": "migrated" if not dry_run else "dry-run",
        })
        if dry_run:
            continue

        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(candidate), str(target))
        ensure_overlay_and_reflection_indexes(target, str(meta.get("analysis_id") or target.name))
        meta = read_json(target / "meta.json")
        rewrite_meta_paths(target, meta)
        write_json(target / "meta.json", meta)

    if operations and not dry_run:
        write_analysis_indexes(project, agent_home=agent_home)
    return operations


def discover_projects(agent_home: Path) -> list[str]:
    projects_root = agent_home / "memory" / "projects"
    if not projects_root.exists():
        return []
    return sorted(path.name for path in projects_root.iterdir() if path.is_dir())


def main() -> int:
    parser = argparse.ArgumentParser(description="Migrate legacy Augur analysis runs from time-first to sha-first layout.")
    parser.add_argument("--agent-home", action="append", default=[], help="Explicit agent home to migrate. May be passed multiple times.")
    parser.add_argument("--agents-root", type=Path, default=Path("/kord/agents"), help="Scan this root for agent homes when --agent-home is omitted.")
    parser.add_argument("--project", action="append", default=[], help="Restrict migration to one or more project slugs.")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    agent_homes = [Path(path).expanduser().resolve() for path in args.agent_home]
    if not agent_homes:
        if args.agents_root.exists():
            agent_homes = sorted(path.resolve() for path in args.agents_root.iterdir() if path.is_dir())
    results: list[dict[str, str]] = []
    for agent_home in agent_homes:
        projects = args.project or discover_projects(agent_home)
        for project in projects:
            results.extend(migrate_project(project, agent_home, dry_run=args.dry_run))

    print(json.dumps({"operations": results}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
