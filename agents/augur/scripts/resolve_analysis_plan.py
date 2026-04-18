#!/usr/bin/env python3
"""Resolve Augur semantic execution defaults from deterministic drift signals.

This script is the source of truth for choosing:
- analysis_mode
- default bundle_mode
- base analysis context

It wraps compute_blast_radius.py so callers do not need to duplicate mode policy.
"""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Resolve deterministic Augur analysis plan")
    parser.add_argument("repo_root", help="Repository root to analyze")
    parser.add_argument("--project", required=True, help="Project slug")
    parser.add_argument("--agent-home", required=True, help="Agent home directory")
    parser.add_argument("--current-sha", help="Optional current commit SHA to forward to blast computation")
    parser.add_argument("--previous-sha", help="Optional previous commit SHA to forward to blast computation")
    parser.add_argument(
        "--analysis-mode",
        default="auto",
        choices=["auto", "full", "incremental", "skip"],
        help="Explicit analysis mode override or auto resolution",
    )
    parser.add_argument(
        "--bundle-mode",
        default="auto",
        help="Explicit bundle mode override or auto resolution",
    )
    return parser.parse_args()


def run_blast(args: argparse.Namespace) -> dict[str, Any]:
    cmd = [
        "python3",
        str(ROOT / "scripts" / "compute_blast_radius.py"),
        str(Path(args.repo_root).resolve()),
        "--project",
        args.project,
        "--agent-home",
        str(Path(args.agent_home).resolve()),
    ]
    if args.current_sha:
        cmd.extend(["--current-sha", args.current_sha])
    if args.previous_sha:
        cmd.extend(["--previous-sha", args.previous_sha])
    payload = subprocess.check_output(cmd, text=True).strip()
    return json.loads(payload)


def normalize_analysis_mode(raw: str | None) -> str:
    value = str(raw or "").strip().lower()
    if value in {"full", "incremental", "skip"}:
        return value
    return "full"


def resolve_bundle_mode(raw: str | None, analysis_mode: str) -> str:
    _ = analysis_mode
    value = str(raw or "").strip().lower()
    if value in {"", "auto", "default"}:
        return "evidence-driven"
    return "evidence-driven"


def main() -> int:
    args = parse_args()
    blast = run_blast(args)
    computed_analysis_mode = normalize_analysis_mode(blast.get("mode"))

    requested_analysis_mode = str(args.analysis_mode or "auto").strip().lower()
    if requested_analysis_mode in {"full", "incremental", "skip"}:
        analysis_mode = requested_analysis_mode
        mode_source = "override"
    else:
        analysis_mode = computed_analysis_mode
        mode_source = "blast"

    bundle_mode = resolve_bundle_mode(args.bundle_mode, analysis_mode)
    bundle_source = "override" if str(args.bundle_mode or "").strip().lower() not in {"", "auto", "default"} else "policy"

    payload = {
        "project": args.project,
        "repo_root": str(Path(args.repo_root).resolve()),
        "agent_home": str(Path(args.agent_home).resolve()),
        "analysis_mode": analysis_mode,
        "analysis_mode_source": mode_source,
        "bundle_mode": bundle_mode,
        "bundle_mode_source": bundle_source,
        "base_analysis_dir": str(blast.get("base_analysis_dir") or ""),
        "analysis_dir": str(blast.get("analysis_dir") or ""),
        "current_sha": str(blast.get("current_sha") or ""),
        "previous_sha": str(blast.get("previous_sha") or ""),
        "reasons": blast.get("reasons") or [],
        "blast": blast,
    }
    print(json.dumps(payload))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
