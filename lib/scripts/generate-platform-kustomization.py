#!/usr/bin/env python3
"""Generate platform overlay kustomization.yaml from config registry settings.

Usage:
    python generate-platform-kustomization.py <env> <registry> [--output <path>]
"""

from __future__ import annotations

import argparse
from pathlib import Path

BASE = "../../../../agents/charon/skills/platform/manifests/base"
IMAGES = [
    "agent-base",
    "agent-charon",
    "agent-augur",
    "docs",
    "log-puller",
]


def build_kustomization(env: str, registry: str) -> str:
    lines = [
        "apiVersion: kustomize.config.k8s.io/v1beta1",
        "kind: Kustomization",
        f"namespace: {env}",
        "resources:",
        f"  - {BASE}",
        "images:",
    ]
    for image in IMAGES:
        lines.extend([
            f"  - name: REGISTRY/{image}",
            f"    newName: {registry}/{image}",
        ])
    lines.extend([
        "patches:",
        "  - path: scaling.yaml",
    ])
    if env == "kord":
        lines.append("  - path: agent-backends.yaml")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate platform overlay kustomization.yaml")
    parser.add_argument("env", help="platform environment (e.g. dev, kord, master)")
    parser.add_argument("registry", help="resolved registry host, e.g. registry.kord")
    parser.add_argument("--output", help="output file path")
    args = parser.parse_args()

    content = build_kustomization(args.env, args.registry)
    if args.output:
        Path(args.output).write_text(content, encoding="utf-8")
    else:
        print(content, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
