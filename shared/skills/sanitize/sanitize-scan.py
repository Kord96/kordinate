#!/usr/bin/env python3
"""Scan git diff for secrets and hardcoded config."""

import fnmatch
import os
import re
import subprocess
import sys
from pathlib import Path

import yaml


def load_patterns(script_dir: Path):
    data = yaml.safe_load((script_dir / "patterns.yaml").read_text())
    patterns = [item for item in data if isinstance(item, dict) and "name" in item]
    exclude = []
    for item in data:
        if isinstance(item, dict) and "exclude" in item:
            exclude = item["exclude"]
    return patterns, exclude


def get_diff(repo_path: str | None):
    cmd = ["git", "diff", "HEAD~1..HEAD", "--no-color", "-U0"]
    if repo_path:
        cmd = ["git", "-C", repo_path] + cmd[1:]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    if result.returncode != 0:
      return []

    lines = []
    current_file = None
    line_num = 0
    for line in result.stdout.split("\n"):
        if line.startswith("diff --git"):
            parts = line.split(" b/")
            if len(parts) > 1:
                current_file = parts[1]
        elif line.startswith("@@"):
            match = re.search(r"\+(\d+)", line)
            if match:
                line_num = int(match.group(1)) - 1
        elif line.startswith("+") and not line.startswith("+++"):
            line_num += 1
            if current_file:
                lines.append((current_file, line_num, line[1:]))
    return lines


def should_exclude(filename: str, exclude_patterns: list[str]) -> bool:
    for pattern in exclude_patterns:
        if fnmatch.fnmatch(filename, pattern) or fnmatch.fnmatch(os.path.basename(filename), pattern):
            return True
    return False


def main():
    repo_path = None
    if "--repo" in sys.argv:
        idx = sys.argv.index("--repo")
        if idx + 1 < len(sys.argv):
            repo_path = sys.argv[idx + 1]

    patterns, exclude = load_patterns(Path(__file__).parent)
    diff_lines = get_diff(repo_path)
    if not diff_lines:
        raise SystemExit(0)

    compiled = []
    for item in patterns:
        compiled.append({
            "name": item["name"],
            "regex": re.compile(item["regex"]),
            "severity": item.get("severity", "info"),
            "message": item.get("message", ""),
        })

    findings = []
    for filename, line_num, content in diff_lines:
        if should_exclude(filename, exclude):
            continue
        for pattern in compiled:
            if pattern["regex"].search(content):
                findings.append((filename, line_num, pattern, content.strip()[:120]))

    if not findings:
        raise SystemExit(0)

    for filename, line_num, pattern, snippet in findings:
        print(f"{pattern['severity'].upper()} [{pattern['name']}] {filename}:{line_num} — {pattern['message']}")
        print(f"  {snippet}\n")

    raise SystemExit(1)


if __name__ == "__main__":
    main()
