#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path


def run_git(repo_root: Path, *args: str) -> str:
    cmd = ["git", "-c", f"safe.directory={repo_root}", "-C", str(repo_root), *args]
    result = subprocess.run(cmd, check=True, capture_output=True, text=True)
    return result.stdout.strip()


def slug_repo_name(name: str) -> str:
    return name.replace("/", "--")


def analysis_timestamp() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).strftime("%Y-%m-%dT%H-%M-%SZ")


def sanitize_suffix(value: str | None) -> str:
    raw = (value or "").strip()
    if not raw:
        return ""
    safe = "".join(ch if ch.isalnum() or ch in "-_" else "-" for ch in raw)
    return safe.strip("-_")


def reset_incomplete_run_dir(run_dir: Path) -> None:
    meta_path = run_dir / "meta.json"
    if meta_path.exists():
        try:
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
        except Exception:
            meta = {}
        if isinstance(meta, dict) and bool(((meta.get("validation") or {}).get("passed"))):
            return

    removable = [
        run_dir / "facts",
        run_dir / "stories",
        run_dir / "atlas.json",
        run_dir / "narratives.yaml",
        run_dir / "blast.json",
        run_dir / "meta.json",
    ]
    for path in removable:
        if path.is_dir():
            for child in sorted(path.rglob("*"), reverse=True):
                if child.is_file() or child.is_symlink():
                    child.unlink(missing_ok=True)
                elif child.is_dir():
                    child.rmdir()
            path.rmdir()
        else:
            path.unlink(missing_ok=True)


def build_payload(repo_root: Path, agent_home: Path, project: str | None, run_suffix: str | None = None) -> dict[str, str]:
    repo_root = repo_root.resolve()
    sha = run_git(repo_root, "rev-parse", "HEAD")
    commit_time = run_git(repo_root, "show", "-s", "--format=%ct", sha)
    project_name = slug_repo_name(project or repo_root.name)
    project_mem = agent_home / "memory" / "projects" / project_name
    analysis = project_mem / "analysis"
    sha_dir = analysis / sha
    run_id = analysis_timestamp()
    safe_suffix = sanitize_suffix(run_suffix)
    if safe_suffix:
        run_id = f"{run_id}--{safe_suffix[-12:]}"
    run_dir = sha_dir / run_id
    analysis.mkdir(parents=True, exist_ok=True)
    sha_dir.mkdir(parents=True, exist_ok=True)
    run_dir.mkdir(parents=True, exist_ok=True)
    reset_incomplete_run_dir(run_dir)
    latest = analysis / "latest.json"
    return {
        "ROOT": str(repo_root),
        "PROJECT": project_name,
        "CURRENT_SHA": sha,
        "CURRENT_TIME": commit_time,
        "ANALYSIS_ID": run_id,
        "PROJECT_MEM": str(project_mem),
        "ANALYSIS": str(analysis),
        "SHA_DIR": str(sha_dir),
        "LATEST": str(latest),
        "RUN": str(run_dir),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Prepare Augur run-scoped analysis directory.")
    parser.add_argument("repo_root", help="Repository root to analyze")
    parser.add_argument("--agent-home", default=os.environ.get("AGENT_HOME_DIR", ""), help="Agent home directory")
    parser.add_argument("--project", default=None, help="Optional explicit project slug")
    parser.add_argument("--run-suffix", default=None, help="Optional unique suffix to isolate concurrent runs")
    parser.add_argument("--shell", action="store_true", help="Print shell exports")
    args = parser.parse_args()

    if not args.agent_home:
        raise SystemExit("AGENT_HOME_DIR or --agent-home is required")

    payload = build_payload(Path(args.repo_root), Path(args.agent_home), args.project, args.run_suffix)
    if args.shell:
        for key, value in payload.items():
            print(f"export {key}={json.dumps(value)}")
    else:
        print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
