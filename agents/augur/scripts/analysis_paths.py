#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ANALYSIS_ID_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}-\d{2}-\d{2}Z(?:--[A-Za-z0-9_-]+)?$")
LEGACY_ANALYSIS_ID_RE = re.compile(r"^\d+-[0-9a-f]{7,40}(?:-[A-Za-z0-9_-]+)?$")


def agent_home_dir(explicit: str | Path | None = None) -> Path:
    if explicit:
        return Path(explicit).expanduser().resolve()
    env_home = os.environ.get("AGENT_HOME_DIR", "").strip()
    if env_home:
        return Path(env_home).expanduser().resolve()
    return Path("/kord/augur")


def slug_repo_name(name: str) -> str:
    return name.replace("/", "--")


def slug_repo_root(repo_root: Path) -> str:
    return slug_repo_name(repo_root.name)


def project_memory_dir(project: str, agent_home: str | Path | None = None) -> Path:
    return agent_home_dir(agent_home) / "memory" / "projects" / slug_repo_name(project)


def project_analysis_dir(project: str, agent_home: str | Path | None = None) -> Path:
    return project_memory_dir(project, agent_home) / "analysis"


def latest_analysis_pointer_path(project: str, agent_home: str | Path | None = None) -> Path:
    return project_analysis_dir(project, agent_home) / "latest.json"


def _sanitize_suffix(value: str | None) -> str:
    raw = (value or "").strip()
    if not raw:
        return ""
    safe = "".join(ch if ch.isalnum() or ch in "-_" else "-" for ch in raw)
    safe = safe.strip("-_")
    return safe


def analysis_dir(project: str, analysis_key: str, agent_home: str | Path | None = None) -> Path:
    return project_analysis_dir(project, agent_home) / analysis_key


def analysis_timestamp() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).strftime("%Y-%m-%dT%H-%M-%SZ")


def analysis_id(timestamp: str | None = None, suffix: str | None = None) -> str:
    base = (timestamp or "").strip() or analysis_timestamp()
    safe_suffix = _sanitize_suffix(suffix)
    return f"{base}--{safe_suffix}" if safe_suffix else base


def analysis_dir_for_commit(project: str, sha: str, commit_time: str | int | None = None, agent_home: str | Path | None = None) -> Path:
    existing = find_analysis_dir_for_sha(project, sha, agent_home)
    if existing is not None:
        return existing
    return analysis_dir(project, analysis_id(), agent_home)


def analysis_meta_path(project: str, analysis_key: str, agent_home: str | Path | None = None) -> Path:
    return analysis_dir(project, analysis_key, agent_home) / "meta.json"


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def read_latest_analysis_pointer(project: str, agent_home: str | Path | None = None) -> dict[str, Any] | None:
    pointer = latest_analysis_pointer_path(project, agent_home)
    if not pointer.exists():
        return None
    payload = read_json(pointer)
    return payload if isinstance(payload, dict) else None


def write_latest_analysis_pointer(project: str, analysis_key: str, sha: str, commit_time: str | int | None = None, agent_home: str | Path | None = None) -> Path:
    pointer = latest_analysis_pointer_path(project, agent_home)
    write_json(
        pointer,
        {
            "analysis_id": analysis_key,
            "analysis_dir": str(analysis_dir(project, analysis_key, agent_home)),
            "sha": sha,
            "commit_time": str(commit_time or ""),
        },
    )
    return pointer


def find_analysis_dir_for_sha(project: str, sha: str, agent_home: str | Path | None = None) -> Path | None:
    sha_key = (sha or "").strip()[:40]
    if not sha_key:
        return None
    matches: list[tuple[str, Path]] = []
    for path, meta in iter_analysis_meta(project, agent_home):
        analyzed_sha = str(meta.get("sha") or "").strip()[:40]
        if analyzed_sha != sha_key:
            continue
        sort_key = str(meta.get("analyzed_at") or path.name)
        matches.append((sort_key, path))
    matches.sort(key=lambda item: item[0], reverse=True)
    return matches[0][1] if matches else None


def iter_analysis_dirs(project: str, agent_home: str | Path | None = None) -> list[Path]:
    root = project_analysis_dir(project, agent_home)
    if not root.exists():
        return []
    return sorted(
        [
            path for path in root.iterdir()
            if path.is_dir() and (ANALYSIS_ID_RE.match(path.name) or LEGACY_ANALYSIS_ID_RE.match(path.name))
        ],
        key=lambda path: path.name,
        reverse=True,
    )


def iter_analysis_meta(project: str, agent_home: str | Path | None = None) -> list[tuple[Path, dict[str, Any]]]:
    records: list[tuple[Path, dict[str, Any]]] = []
    for path in iter_analysis_dirs(project, agent_home):
        meta_path = path / "meta.json"
        if not meta_path.exists():
            continue
        payload = read_json(meta_path)
        if isinstance(payload, dict):
            records.append((path, payload))
    return records


def analysis_index_path(project: str, agent_home: str | Path | None = None) -> Path:
    return project_analysis_dir(project, agent_home) / "index.json"


def analysis_by_sha_dir(project: str, agent_home: str | Path | None = None) -> Path:
    return project_analysis_dir(project, agent_home) / "by-sha"


def write_analysis_indexes(project: str, agent_home: str | Path | None = None) -> None:
    records = iter_analysis_meta(project, agent_home)
    summaries: list[dict[str, Any]] = []
    by_sha: dict[str, list[dict[str, Any]]] = {}

    for path, meta in records:
        summary = {
            "analysis_id": str(meta.get("analysis_id") or path.name),
            "analysis_dir": str(path),
            "project": str(meta.get("project") or project),
            "sha": str(meta.get("sha") or ""),
            "commit_time": str(meta.get("commit_time") or ""),
            "base_sha": str(meta.get("base_sha") or ""),
            "base_commit_time": str(meta.get("base_commit_time") or ""),
            "analysis_mode": str(meta.get("analysis_mode") or ""),
            "analyzed_at": str(meta.get("analyzed_at") or ""),
            "execution": meta.get("execution") or {},
            "validation": meta.get("validation") or {},
        }
        summaries.append(summary)
        sha = summary["sha"]
        if sha:
            by_sha.setdefault(sha, []).append(summary)

    write_json(
        analysis_index_path(project, agent_home),
        {
            "project": project,
            "analyses": summaries,
        },
    )
    by_sha_root = analysis_by_sha_dir(project, agent_home)
    if by_sha_root.exists():
        for child in by_sha_root.iterdir():
            if child.is_file():
                child.unlink()
    by_sha_root.mkdir(parents=True, exist_ok=True)
    for sha, items in by_sha.items():
        write_json(
            by_sha_root / f"{sha}.json",
            {
                "project": project,
                "sha": sha,
                "analyses": items,
            },
        )
