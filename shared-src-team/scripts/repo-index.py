#!/usr/bin/env python3
"""Manage the test repo index at /data/repos/index.json.

Usage:
    repo-index.py check <nameWithOwner>    — exit 0 if repo exists, exit 1 if new
    repo-index.py add <nameWithOwner> <language> [--tested-by <agent>]  — clone and register
    repo-index.py list [--untested]        — list all repos (optionally only untested)
    repo-index.py mark-tested <nameWithOwner> <agent>  — record that an agent tested this repo

The index is the single source of truth for what repos exist. The improve
loop checks it instead of scanning the filesystem.
"""

import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

INDEX_PATH = Path("/data/repos/index.json")
REPOS_DIR = Path("/data/repos")


def load_index() -> list[dict]:
    if INDEX_PATH.exists():
        return json.loads(INDEX_PATH.read_text())
    return []


def save_index(index: list[dict]):
    REPOS_DIR.mkdir(parents=True, exist_ok=True)
    INDEX_PATH.write_text(json.dumps(index, indent=2) + "\n")


def find_repo(index: list[dict], name: str) -> dict | None:
    for entry in index:
        if entry["nameWithOwner"] == name:
            return entry
    return None


def cmd_check(name: str):
    index = load_index()
    entry = find_repo(index, name)
    if entry:
        print(json.dumps(entry))
        sys.exit(0)
    else:
        sys.exit(1)


def cmd_add(name: str, language: str, tested_by: str | None = None):
    index = load_index()
    if find_repo(index, name):
        print(f"Already exists: {name}", file=sys.stderr)
        sys.exit(1)

    # Clone
    owner, repo = name.split("/", 1)
    path = REPOS_DIR / f"{owner}--{repo}"

    if not path.exists():
        result = subprocess.run(
            ["git", "clone", "--depth", "1", f"https://github.com/{name}.git", str(path)],
            capture_output=True, text=True
        )
        if result.returncode != 0:
            print(f"Clone failed: {result.stderr}", file=sys.stderr)
            sys.exit(1)

    entry = {
        "nameWithOwner": name,
        "path": str(path),
        "language": language,
        "cloned_at": datetime.now().isoformat(),
        "tested_by": [tested_by] if tested_by else [],
    }
    index.append(entry)
    save_index(index)
    print(json.dumps(entry))


def cmd_list(untested: bool = False):
    index = load_index()
    if untested:
        index = [e for e in index if not e.get("tested_by")]
    for entry in index:
        tested = ", ".join(entry.get("tested_by", [])) or "untested"
        print(f"{entry['nameWithOwner']:<40} {entry['language']:<12} {tested}")
    print(f"\n{len(index)} repos", file=sys.stderr)


def cmd_mark_tested(name: str, agent: str):
    index = load_index()
    entry = find_repo(index, name)
    if not entry:
        print(f"Not found: {name}", file=sys.stderr)
        sys.exit(1)
    if agent not in entry.get("tested_by", []):
        entry.setdefault("tested_by", []).append(agent)
    save_index(index)
    print(f"Marked {name} as tested by {agent}")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    cmd = sys.argv[1]
    if cmd == "check" and len(sys.argv) >= 3:
        cmd_check(sys.argv[2])
    elif cmd == "add" and len(sys.argv) >= 4:
        tested_by = None
        if "--tested-by" in sys.argv:
            idx = sys.argv.index("--tested-by")
            tested_by = sys.argv[idx + 1] if idx + 1 < len(sys.argv) else None
        cmd_add(sys.argv[2], sys.argv[3], tested_by)
    elif cmd == "list":
        cmd_list(untested="--untested" in sys.argv)
    elif cmd == "mark-tested" and len(sys.argv) >= 4:
        cmd_mark_tested(sys.argv[2], sys.argv[3])
    else:
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
