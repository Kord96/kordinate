#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path
from typing import Any

import yaml


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def copy_tree(src: Path, dst: Path) -> None:
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)


def copy_file(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def normalize_docs_meta(meta: dict[str, Any], project: str, analysis_id: str) -> dict[str, Any]:
    repository = meta.get("repository") or {}
    agent = meta.get("agent") or {}
    analysis = meta.get("analysis") or {}
    return {
        "project": project,
        "analysis_id": analysis_id,
        "request_id": str(meta.get("request_id") or ""),
        "repository": repository if isinstance(repository, dict) else {},
        "agent": agent if isinstance(agent, dict) else {},
        "commit_sha": str(repository.get("commit") or meta.get("sha") or ""),
        "commit_time": str(repository.get("commit_time") or meta.get("commit_time") or ""),
        "analyzed_at": str(analysis.get("analyzed_at") or meta.get("analyzed_at") or ""),
        "source": "augur",
        "status": "ready" if bool(((analysis.get("validation") or {}).get("passed"))) else "pending",
        "analysis": analysis if isinstance(analysis, dict) else {},
        "validation": analysis.get("validation") if isinstance(analysis.get("validation"), dict) else {},
    }


def render_current_pointer(project: str, analysis_id: str) -> dict[str, Any]:
    return {
        "project": project,
        "default_analysis_id": analysis_id,
        "default_overlay_id": None,
        "published_at": read_json_timestamp(),
    }


def read_json_timestamp() -> str:
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_narratives(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"version": "1", "narratives": []}
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {"version": "1", "narratives": []}


def export_analysis(analysis_dir: Path, docs_store_root: Path, publish_current: bool) -> Path:
    analysis_dir = analysis_dir.resolve()
    meta_path = analysis_dir / "meta.json"
    atlas_path = analysis_dir / "atlas.json"
    stories_dir = analysis_dir / "stories"
    narratives_path = analysis_dir / "narratives.yaml"
    if not meta_path.exists():
        raise SystemExit(f"meta.json not found at {meta_path}")
    if not atlas_path.exists():
        raise SystemExit(f"atlas.json not found at {atlas_path}")
    if not stories_dir.exists():
        raise SystemExit(f"stories/ not found at {stories_dir}")
    if not narratives_path.exists():
        raise SystemExit(f"narratives.yaml not found at {narratives_path}")

    meta = read_json(meta_path)
    project = str(((meta.get("repository") or {}).get("project")) or meta.get("project") or analysis_dir.parents[1].name)
    analysis_id = str(((meta.get("analysis") or {}).get("id")) or meta.get("analysis_id") or analysis_dir.name)

    docs_analysis_root = docs_store_root / "projects" / project / "analyses" / analysis_id
    docs_analysis_root.mkdir(parents=True, exist_ok=True)

    copy_file(atlas_path, docs_analysis_root / "atlas.json")
    copy_tree(stories_dir, docs_analysis_root / "stories")
    copy_file(narratives_path, docs_analysis_root / "narratives.yaml")
    write_json(docs_analysis_root / "meta.json", normalize_docs_meta(meta, project, analysis_id))

    if publish_current:
        write_json(
            docs_store_root / "projects" / project / "published" / "current.json",
            render_current_pointer(project, analysis_id),
        )

    return docs_analysis_root


def main() -> int:
    parser = argparse.ArgumentParser(description="Export one accepted Augur analysis into the docs-store shape used by kordinate-docs.")
    parser.add_argument("analysis_dir", type=Path)
    parser.add_argument("--docs-store-root", type=Path, default=Path("/kord/docs-store"))
    parser.add_argument("--publish-current", action="store_true")
    args = parser.parse_args()

    exported = export_analysis(args.analysis_dir, args.docs_store_root.resolve(), args.publish_current)
    print(json.dumps({"exported_to": str(exported)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
