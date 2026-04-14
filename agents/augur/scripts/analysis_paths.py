#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any


ANALYSIS_ID_RE = re.compile(r"^\d+-[0-9a-f]{7,40}$")


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


def analysis_id(commit_time: str | int | None, sha: str) -> str:
    timestamp = str(commit_time or "0").strip() or "0"
    sha_key = (sha or "workspace").strip()[:40] or "workspace"
    return f"{timestamp}-{sha_key}"


def analysis_dir(project: str, analysis_key: str, agent_home: str | Path | None = None) -> Path:
    return project_analysis_dir(project, agent_home) / analysis_key


def analysis_dir_for_commit(project: str, sha: str, commit_time: str | int | None = None, agent_home: str | Path | None = None) -> Path:
    if commit_time is None:
        existing = find_analysis_dir_for_sha(project, sha, agent_home)
        if existing is not None:
            return existing
        return analysis_dir(project, (sha or "workspace").strip()[:40] or "workspace", agent_home)
    return analysis_dir(project, analysis_id(commit_time, sha), agent_home)


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
    root = project_analysis_dir(project, agent_home)
    if not root.exists():
        return None

    direct = root / sha_key
    if direct.exists():
        return direct

    pattern = re.compile(rf"^\d+-{re.escape(sha_key)}$")
    matches = sorted(
        [path for path in root.iterdir() if path.is_dir() and pattern.match(path.name)],
        key=lambda path: path.name,
        reverse=True,
    )
    return matches[0] if matches else None


def iter_analysis_dirs(project: str, agent_home: str | Path | None = None) -> list[Path]:
    root = project_analysis_dir(project, agent_home)
    if not root.exists():
        return []
    return sorted(
        [
            path for path in root.iterdir()
            if path.is_dir() and ANALYSIS_ID_RE.match(path.name)
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
