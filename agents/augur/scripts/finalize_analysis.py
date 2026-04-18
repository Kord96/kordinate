#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from analysis_paths import write_analysis_indexes, write_json, write_latest_analysis_pointer


ROOT = Path(__file__).resolve().parents[1]
ATLAS_SCHEMA = ROOT / "schemas" / "atlas-schema.md"
FACTS_SCHEMA = ROOT / "schemas" / "facts-schema.md"
STORY_SCHEMA = ROOT / "schemas" / "story-schema.md"
NARRATIVES_SCHEMA = ROOT / "schemas" / "narratives-schema.md"
META_SCHEMA = ROOT / "schemas" / "meta-schema.md"


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_env(name: str) -> str:
    return str((os.environ.get(name) or "")).strip()


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def relative_to_run_root(analysis_dir: Path, path: Path) -> str:
    try:
        return str(path.resolve().relative_to(analysis_dir.resolve()))
    except Exception:
        return str(path.resolve())


def latest_repair_iteration(analysis_dir: Path) -> dict[str, Any]:
    repair_log_path = analysis_dir / "repair-log.json"
    if not repair_log_path.exists():
        return {}
    payload = read_json(repair_log_path)
    iterations = payload.get("iterations") or []
    if not isinstance(iterations, list) or not iterations:
        return {}
    latest = iterations[-1]
    return latest if isinstance(latest, dict) else {}


def analysis_context(analysis_dir: Path) -> tuple[str, str, Path]:
    analysis_id = analysis_dir.name
    if analysis_dir.parent.name == "analysis":
        project = analysis_dir.parents[1].name
        agent_home = analysis_dir.parents[4]
        return project, analysis_id, agent_home
    if analysis_dir.parent.parent.name == "analysis":
        project = analysis_dir.parents[2].name
        agent_home = analysis_dir.parents[5]
        return project, analysis_id, agent_home
    raise SystemExit(f"analysis directory is not under memory/projects/<project>/analysis/<sha>/<id>: {analysis_dir}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Finalize an Augur analysis directory by writing meta.json and updating latest.json.")
    parser.add_argument("analysis_dir", type=Path)
    parser.add_argument("--validation-token", default="")
    parser.add_argument("--validation-attempts", type=int, default=0)
    args = parser.parse_args()

    analysis_dir = args.analysis_dir.resolve()
    atlas_path = analysis_dir / "atlas.json"
    if not atlas_path.exists():
        raise SystemExit(f"atlas.json not found at {atlas_path}")

    atlas = read_json(atlas_path)
    blast_path = analysis_dir / "blast.json"
    blast = read_json(blast_path) if blast_path.exists() else {}
    latest_repair = latest_repair_iteration(analysis_dir)
    existing_meta_path = analysis_dir / "meta.json"
    existing_meta = read_json(existing_meta_path) if existing_meta_path.exists() else {}

    latest_status = str(latest_repair.get("status") or "")
    validation_passed = latest_status == "valid"
    if latest_status and not validation_passed:
        raise SystemExit(f"cannot finalize analysis with repair-log status '{latest_status}'")
    if not latest_status and not existing_meta.get("validation", {}).get("passed"):
        raise SystemExit("cannot finalize analysis without a valid repair-log.json or an already-passed meta.json")

    project_slug, analysis_id, agent_home = analysis_context(analysis_dir)
    project_name = str(atlas.get("project") or existing_meta.get("project") or project_slug)
    sha = str(atlas.get("metadata", {}).get("analyzed_at_sha") or existing_meta.get("sha") or blast.get("current_sha") or "")
    commit_time = str(blast.get("current_commit_time") or existing_meta.get("commit_time") or "")
    base_sha = str(blast.get("previous_sha") or existing_meta.get("base_sha") or atlas.get("metadata", {}).get("base_sha") or "")
    base_commit_time = str(blast.get("previous_commit_time") or existing_meta.get("base_commit_time") or atlas.get("metadata", {}).get("base_commit_time") or "")
    analysis_mode = str(atlas.get("metadata", {}).get("analysis_mode") or existing_meta.get("analysis_mode") or blast.get("mode") or "")

    facts_index = analysis_dir / "facts" / "index.json"
    stories_dir = analysis_dir / "stories"
    narratives_path = analysis_dir / "narratives.yaml"
    overlays_dir = analysis_dir / "overlays"
    reflections_dir = analysis_dir / "reflections"
    overlays_index = overlays_dir / "index.json"
    reflections_index = reflections_dir / "index.json"
    overlays_dir.mkdir(parents=True, exist_ok=True)
    reflections_dir.mkdir(parents=True, exist_ok=True)
    if not overlays_index.exists():
        write_json(overlays_index, {"analysis_id": analysis_id, "overlays": []})
    if not reflections_index.exists():
        write_json(reflections_index, {"analysis_id": analysis_id, "reflections": []})
    meta = {
        "project": project_name,
        "analysis_id": analysis_id,
        "sha": sha,
        "commit_time": commit_time,
        "analysis_mode": analysis_mode,
        "base_sha": base_sha,
        "base_commit_time": base_commit_time,
        "analyzed_at": str(existing_meta.get("analyzed_at") or now_iso()),
        "blast": {
            "mode": blast.get("mode", ""),
            "tier": blast.get("tier", 0),
            "reasons": blast.get("reasons", []),
            "affected_components": blast.get("affected_components", []),
            "affected_flows": blast.get("affected_flows", []),
            "affected_state": blast.get("affected_state", []),
            "affected_dependencies": blast.get("affected_dependencies", []),
            "affected_concepts": blast.get("affected_concepts", []),
        },
        "artifacts": {
            "root": ".",
            "atlas": relative_to_run_root(analysis_dir, atlas_path),
            "facts_index": relative_to_run_root(analysis_dir, facts_index) if facts_index.exists() else "",
            "stories_dir": relative_to_run_root(analysis_dir, stories_dir) if stories_dir.exists() else "",
            "narratives": relative_to_run_root(analysis_dir, narratives_path) if narratives_path.exists() else "",
            "blast": relative_to_run_root(analysis_dir, blast_path) if blast_path.exists() else "",
            "overlays_dir": relative_to_run_root(analysis_dir, overlays_dir),
            "overlays_index": relative_to_run_root(analysis_dir, overlays_index),
            "reflections_dir": relative_to_run_root(analysis_dir, reflections_dir),
            "reflections_index": relative_to_run_root(analysis_dir, reflections_index),
        },
        "schemas": {
            "facts": str(FACTS_SCHEMA),
            "atlas": str(ATLAS_SCHEMA),
            "story": str(STORY_SCHEMA),
            "narratives": str(NARRATIVES_SCHEMA),
            "meta": str(META_SCHEMA),
        },
        "execution": {
            "agent": read_env("AUGUR_AGENT_NAME"),
            "specialization": read_env("AUGUR_AGENT_SPECIALIZATION"),
            "provider": read_env("AUGUR_PROVIDER"),
            "runtime": read_env("AUGUR_RUNTIME_KIND"),
            "model": read_env("AUGUR_MODEL"),
            "bundle_mode": read_env("AUGUR_BUNDLE_MODE"),
            "agent_contract_version": read_env("AUGUR_AGENT_CONTRACT_VERSION"),
            "runtime_profile_version": read_env("AUGUR_RUNTIME_PROFILE_VERSION"),
        },
        "validation": {
            "passed": validation_passed or bool(existing_meta.get("validation", {}).get("passed")),
            "attempts": int(latest_repair.get("iteration") or args.validation_attempts or existing_meta.get("validation", {}).get("attempts") or 0),
            "token": str(args.validation_token or existing_meta.get("validation", {}).get("token") or ""),
        },
    }

    write_json(existing_meta_path, meta)
    write_latest_analysis_pointer(project_slug, analysis_id, sha, commit_time, agent_home=agent_home, analysis_path=analysis_dir)
    write_analysis_indexes(project_slug, agent_home=agent_home)

    print(json.dumps(meta, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
