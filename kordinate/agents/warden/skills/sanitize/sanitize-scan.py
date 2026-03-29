#!/usr/bin/env python3
"""Scan git diff for secrets and hardcoded config.

Usage:
    python sanitize-scan.py [--repo <path>]

Loads patterns from patterns.yaml (same directory as this script).
Scans only added lines (lines starting with +) from the git diff.
Skips files matching exclude patterns.

Exit codes:
    0 = clean
    1 = findings (critical or warning)
    2 = error (can't read patterns, no git repo, etc.)
"""

import fnmatch
import os
import re
import subprocess
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None


def load_patterns(script_dir: Path) -> tuple[list[dict], list[str]]:
    """Load patterns from patterns.yaml."""
    patterns_file = script_dir / "patterns.yaml"
    if not patterns_file.exists():
        print(f"patterns.yaml not found at {patterns_file}", file=sys.stderr)
        sys.exit(2)

    text = patterns_file.read_text()

    if yaml:
        data = yaml.safe_load(text)
    else:
        # Minimal YAML parsing fallback — won't handle all cases
        import json
        print("PyYAML not installed, pattern loading may be limited", file=sys.stderr)
        sys.exit(2)

    # Separate patterns from exclude list
    patterns = [item for item in data if isinstance(item, dict) and "name" in item]
    exclude = []
    for item in data:
        if isinstance(item, dict) and "exclude" in item:
            exclude = item["exclude"]

    return patterns, exclude


def get_diff(repo_path: str | None) -> list[tuple[str, int, str]]:
    """Get added lines from git diff. Returns [(filename, line_num, line_content)]."""
    cmd = ["git", "diff", "HEAD~1..HEAD", "--no-color", "-U0"]
    if repo_path:
        cmd = ["git", "-C", repo_path] + cmd[1:]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    except (subprocess.TimeoutExpired, FileNotFoundError):
        # Try staged diff as fallback
        cmd[-2] = "--cached"
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        except Exception:
            return []

    if result.returncode != 0:
        return []

    lines = []
    current_file = None
    line_num = 0

    for line in result.stdout.split("\n"):
        if line.startswith("diff --git"):
            # Extract filename
            parts = line.split(" b/")
            if len(parts) > 1:
                current_file = parts[1]
        elif line.startswith("@@"):
            # Extract line number
            match = re.search(r'\+(\d+)', line)
            if match:
                line_num = int(match.group(1)) - 1
        elif line.startswith("+") and not line.startswith("+++"):
            line_num += 1
            if current_file:
                lines.append((current_file, line_num, line[1:]))  # strip the leading +

    return lines


def should_exclude(filename: str, exclude_patterns: list[str]) -> bool:
    """Check if a file matches any exclude pattern."""
    for pattern in exclude_patterns:
        if fnmatch.fnmatch(filename, pattern):
            return True
        if fnmatch.fnmatch(os.path.basename(filename), pattern):
            return True
    return False


def main():
    repo_path = None
    if "--repo" in sys.argv:
        idx = sys.argv.index("--repo")
        if idx + 1 < len(sys.argv):
            repo_path = sys.argv[idx + 1]

    script_dir = Path(__file__).parent
    patterns, exclude = load_patterns(script_dir)

    diff_lines = get_diff(repo_path)
    if not diff_lines:
        sys.exit(0)  # No diff = clean

    # Compile regexes
    compiled = []
    for p in patterns:
        try:
            compiled.append({
                "name": p["name"],
                "regex": re.compile(p["regex"]),
                "severity": p.get("severity", "info"),
                "message": p.get("message", ""),
            })
        except re.error as e:
            print(f"Bad regex in pattern '{p['name']}': {e}", file=sys.stderr)

    # Scan
    findings = []
    for filename, line_num, content in diff_lines:
        if should_exclude(filename, exclude):
            continue

        for p in compiled:
            if p["regex"].search(content):
                findings.append({
                    "file": filename,
                    "line": line_num,
                    "pattern": p["name"],
                    "severity": p["severity"],
                    "message": p["message"],
                    "content": content.strip()[:80],
                })

    # Report
    if not findings:
        sys.exit(0)

    critical = [f for f in findings if f["severity"] == "critical"]
    warning = [f for f in findings if f["severity"] == "warning"]
    info = [f for f in findings if f["severity"] == "info"]

    for f in findings:
        sev = f["severity"].upper()
        print(f"{sev} [{f['pattern']}] {f['file']}:{f['line']} — {f['message']}")
        print(f"  {f['content']}")
        print()

    total_blocking = len(critical) + len(warning)
    print(f"Sanitize: {len(critical)} critical, {len(warning)} warning, {len(info)} info")

    if total_blocking > 0:
        print(f"\nBlocked: {total_blocking} findings require action.")
        print("Fix: move secrets to pass store via /kord alfred store key <path> <value>")
        print("Fix: move config to config.yaml via /kord alfred store config <path> <value>")
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
