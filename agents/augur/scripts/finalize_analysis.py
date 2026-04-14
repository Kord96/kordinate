#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from analysis_paths import write_json, write_latest_analysis_pointer


ROOT = Path(__file__).resolve().parents[1]
ATLAS_SCHEMA = ROOT / "schemas" / "atlas-schema.md"
FACTS_SCHEMA = ROOT / "schemas" / "facts-schema.md"
STORY_SCHEMA = ROOT / "schemas" / "story-schema.md"
NARRATIVES_SCHEMA = ROOT / "schemas" / "narratives-schema.md"
META_SCHEMA = ROOT / "schemas" / "meta-schema.md"


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def analysis_context(analysis_dir: Path) -> tuple[str, str]:
    try:
        project = analysis_dir.parents[1].name
        analysis_id = analysis_dir.name
    except IndexError as exc:
        raise SystemExit(f"analysis directory is not under memory/projects/<project>/analysis/<id>: {analysis_dir}") from exc
    return project, analysis_id


def parse_analysis_id(analysis_id: str) -> tuple[str, str]:
    if "-" not in analysis_id:
        return "", ""
    commit_time, sha = analysis_id.split("-", 1)
    return commit_time, sha


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
    existing_meta_path = analysis_dir / "meta.json"
    existing_meta = read_json(existing_meta_path) if existing_meta_path.exists() else {}

    project_slug, analysis_id = analysis_context(analysis_dir)
    analysis_commit_time, analysis_sha = parse_analysis_id(analysis_id)
    project_name = str(atlas.get("project") or existing_meta.get("project") or project_slug)
    sha = str(atlas.get("metadata", {}).get("analyzed_at_sha") or existing_meta.get("sha") or analysis_sha)
    commit_time = str(blast.get("current_commit_time") or existing_meta.get("commit_time") or analysis_commit_time)
    base_sha = str(blast.get("previous_sha") or existing_meta.get("base_sha") or atlas.get("metadata", {}).get("base_sha") or "")
    base_commit_time = str(blast.get("previous_commit_time") or existing_meta.get("base_commit_time") or atlas.get("metadata", {}).get("base_commit_time") or "")
    analysis_mode = str(atlas.get("metadata", {}).get("analysis_mode") or existing_meta.get("analysis_mode") or blast.get("mode") or "")

    facts_index = analysis_dir / "facts" / "index.json"
    stories_dir = analysis_dir / "stories"
    narratives_path = analysis_dir / "narratives.yaml"
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
            "root": str(analysis_dir),
            "atlas": str(atlas_path),
            "facts_index": str(facts_index) if facts_index.exists() else "",
            "stories_dir": str(stories_dir) if stories_dir.exists() else "",
            "narratives": str(narratives_path) if narratives_path.exists() else "",
            "blast": str(blast_path) if blast_path.exists() else "",
        },
        "schemas": {
            "facts": str(FACTS_SCHEMA),
            "atlas": str(ATLAS_SCHEMA),
            "story": str(STORY_SCHEMA),
            "narratives": str(NARRATIVES_SCHEMA),
            "meta": str(META_SCHEMA),
        },
        "validation": {
            "passed": True,
            "attempts": max(args.validation_attempts, 1) if args.validation_token else max(args.validation_attempts, 0),
            "token": args.validation_token,
        },
    }

    write_json(existing_meta_path, meta)
    write_latest_analysis_pointer(project_slug, analysis_id, sha, commit_time)

    print(json.dumps(meta, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
