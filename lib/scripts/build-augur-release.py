#!/usr/bin/env python3
"""Build an Augur release from the standalone Augur repo checkout."""

from __future__ import annotations

import argparse
import os
import subprocess
from pathlib import Path


DEFAULT_AUGUR_REPO = Path("/kord/workstation/home/project/augur")


def parse_args() -> tuple[argparse.Namespace, list[str]]:
    parser = argparse.ArgumentParser(
        description="Build a publishable Augur release from the standalone Augur repo checkout"
    )
    parser.add_argument(
        "--source-root",
        default=os.environ.get("AUGUR_REPO_HOME", str(DEFAULT_AUGUR_REPO)),
        help="Standalone Augur repo root; defaults to $AUGUR_REPO_HOME or /kord/workstation/home/project/augur",
    )
    args, passthrough = parser.parse_known_args()
    return args, passthrough


def main() -> int:
    args, passthrough = parse_args()
    source_root = Path(args.source_root).resolve()
    script_path = source_root / "scripts" / "build" / "build_release_artifact.py"

    if not source_root.exists():
        raise SystemExit(f"Augur repo root not found: {source_root}")
    if not script_path.exists():
        raise SystemExit(f"Augur release builder not found: {script_path}")

    result = subprocess.run(["python3", str(script_path), *passthrough], cwd=source_root)
    return int(result.returncode)


if __name__ == "__main__":
    raise SystemExit(main())
