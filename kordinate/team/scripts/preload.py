#!/usr/bin/env python3
"""Generate a merged preload file for an agent's boot.

Usage:
    python preload.py <agent-name> [kordinate-home]

Reads KORD.json, filters file entries where preload matches the agent name
or "all", concatenates the file contents, and writes to stdout.

The boot skill pipes this to a temp file that the agent reads in one shot
instead of scanning hundreds of frontmatter blocks.

Skips IDENTITY.md files (already loaded as agent definition).
"""

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

    # Filter: file entries where preload matches agent or "all"
    preload_entries = [
        e for e in entries
        if e.get("type") == "file"
        and e.get("preload") in (agent, "all")
        and not e.get("path", "").endswith("IDENTITY.md")  # Skip — already in agent definition
    ]

    if not preload_entries:
        print(f"# No preload files for agent: {agent}", file=sys.stderr)
        sys.exit(0)

    # Concatenate file contents
    loaded = 0
    for entry in preload_entries:
        file_path = home / entry["path"]
        if file_path.exists():
            desc = entry.get("description", "")
            print(f"\n# === {entry['path']} — {desc} ===\n")
            print(file_path.read_text())
            loaded += 1
        else:
            print(f"# MISSING: {entry['path']}", file=sys.stderr)

    print(f"\n# Preloaded {loaded} files for {agent}", file=sys.stderr)


if __name__ == "__main__":
    main()
