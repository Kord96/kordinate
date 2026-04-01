#!/usr/bin/env python3
"""Generate a merged preload file for an agent's boot.

Usage:
    python preload.py <agent-name> [kordinate-home]

Reads KORD.json, filters entries where preload matches the agent name
or "all", concatenates the file contents, and writes to stdout.

Supports two entry types:
  - "file": single file path
  - "dir": glob pattern matching multiple files

Skips IDENTITY.md files (already loaded as agent definition).
"""

import glob as globmod
import json
import os
import sys
from pathlib import Path


def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <agent-name> [kordinate-home]", file=sys.stderr)
        sys.exit(1)

    agent = sys.argv[1]
    home = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(os.environ.get("KORDINATE_HOME", os.path.expanduser("~/.kord")))

    kord_json = home / "KORD.json"
    if not kord_json.exists():
        print(f"KORD.json not found at {kord_json}", file=sys.stderr)
        sys.exit(1)

    entries = json.loads(kord_json.read_text())

    # Collect all file paths to preload: (absolute_path, relative_display_path)
    file_paths: list[tuple[Path, str]] = []

    for entry in entries:
        preload = entry.get("preload")
        if preload not in (agent, "all"):
            continue

        if entry.get("type") == "file":
            path = entry.get("path", "")
            if path.endswith("IDENTITY.md"):
                continue
            abs_path = home / path
            if abs_path.exists():
                file_paths.append((abs_path, path))

        elif entry.get("type") == "dir":
            pattern = entry.get("pattern", "")
            if not pattern:
                continue
            for match in sorted(globmod.glob(str(home / pattern), recursive=True)):
                match_path = Path(match)
                if match_path.is_file() and match_path.name != "IDENTITY.md":
                    file_paths.append((match_path, str(match_path.relative_to(home))))

    if not file_paths:
        print(f"# No preload files for agent: {agent}", file=sys.stderr)
        sys.exit(0)

    # Deduplicate
    seen = set()
    unique: list[tuple[Path, str]] = []
    for abs_path, rel_path in file_paths:
        if rel_path not in seen:
            seen.add(rel_path)
            unique.append((abs_path, rel_path))

    # Concatenate
    loaded = 0
    for abs_path, rel_path in unique:
        print(f"\n# === {rel_path} ===\n")
        print(abs_path.read_text())
        loaded += 1

    print(f"\n# Preloaded {loaded} files for {agent}", file=sys.stderr)


if __name__ == "__main__":
    main()
