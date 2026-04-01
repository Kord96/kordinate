#!/usr/bin/env python3
"""Run ast-grep concept detection using individual rule files.

Usage:
    python run_ast_grep.py <project-root> [--kordinate-home <path>]

Finds all ast-grep.yaml rule files in the concept catalog and runs them
against the target project. Outputs JSON array of matches with ruleId
mapped to concept names.

This avoids the ruleDirs contamination issue where questions.yaml and
other non-rule files in concept directories cause ast-grep to fail.
"""

import glob
import json
import os
import subprocess
import sys
from pathlib import Path


def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <project-root> [--kordinate-home <path>]", file=sys.stderr)
        sys.exit(2)

    project_root = sys.argv[1]
    kordinate_home = os.environ.get("KORDINATE_HOME", os.path.expanduser("~/.kord"))

    # Parse optional --kordinate-home
    if "--kordinate-home" in sys.argv:
        idx = sys.argv.index("--kordinate-home")
        if idx + 1 < len(sys.argv):
            kordinate_home = sys.argv[idx + 1]

    concepts_dir = Path(kordinate_home) / "agents" / "augur" / "memory" / "concepts"

    if not concepts_dir.exists():
        print(f"Concepts directory not found: {concepts_dir}", file=sys.stderr)
        sys.exit(1)

    # Find all ast-grep rule files
    rule_files = sorted(glob.glob(str(concepts_dir / "*/ast-grep.yaml")))

    if not rule_files:
        print("[]")
        return

    all_matches = []
    errors = []

    for rule_file in rule_files:
        try:
            result = subprocess.run(
                ["ast-grep", "scan", "-r", rule_file, project_root, "--json"],
                capture_output=True,
                text=True,
                timeout=30,
            )
            if result.returncode == 0 and result.stdout.strip():
                matches = json.loads(result.stdout)
                if isinstance(matches, list):
                    all_matches.extend(matches)
        except subprocess.TimeoutExpired:
            errors.append(f"Timeout scanning with {Path(rule_file).parent.name}")
        except (json.JSONDecodeError, Exception) as e:
            errors.append(f"Error with {Path(rule_file).parent.name}: {e}")

    if errors:
        print(f"Warnings: {len(errors)} rules had issues", file=sys.stderr)
        for err in errors[:10]:
            print(f"  - {err}", file=sys.stderr)

    print(json.dumps(all_matches))


if __name__ == "__main__":
    main()
