#!/usr/bin/env python3
"""Assemble global KORD.json from agent and team KORD.json files.

Usage:
    python assemble-kord.py <kordinate-home>

Reads:
    <home>/agents/*/KORD.json
    <home>/team/KORD.json

Writes:
    <home>/KORD.json (global manifest)
    <home>/KORD-seed.json (copy for factory reset)
"""

import json
import sys
from pathlib import Path


def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <kordinate-home>")
        sys.exit(1)

    home = Path(sys.argv[1])
    if not home.exists():
        print(f"Not found: {home}")
        sys.exit(1)

    entries = []

    # Collect from agents
    agents_dir = home / "agents"
    if agents_dir.exists():
        for agent_dir in sorted(agents_dir.iterdir()):
            kord_file = agent_dir / "KORD.json"
            if kord_file.exists():
                try:
                    agent_entries = json.loads(kord_file.read_text())
                    entries.extend(agent_entries)
                    print(f"  {agent_dir.name}: {len(agent_entries)} entries")
                except json.JSONDecodeError as e:
                    print(f"  {agent_dir.name}: PARSE ERROR: {e}")

    # Collect from team
    team_file = home / "team" / "KORD.json"
    if team_file.exists():
        try:
            team_entries = json.loads(team_file.read_text())
            entries.extend(team_entries)
            print(f"  team: {len(team_entries)} entries")
        except json.JSONDecodeError as e:
            print(f"  team: PARSE ERROR: {e}")

    # Summary
    skills = [e for e in entries if e.get("type") == "skill"]
    guards = [e for e in entries if e.get("type") == "guard"]
    files = [e for e in entries if e.get("type") == "file"]

    print(f"\nAssembled: {len(entries)} total ({len(skills)} skills, {len(guards)} guards, {len(files)} files)")

    # Write global
    global_path = home / "KORD.json"
    global_path.write_text(json.dumps(entries, indent=2) + "\n")
    print(f"Wrote: {global_path}")

    # Write seed only if it doesn't exist (factory reset baseline)
    seed_path = home / "KORD-seed.json"
    if not seed_path.exists():
        seed_path.write_text(json.dumps(entries, indent=2) + "\n")
        print(f"Wrote: {seed_path} (first install)")
    else:
        print(f"Kept: {seed_path} (already exists)")


if __name__ == "__main__":
    main()
