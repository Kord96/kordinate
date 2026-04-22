#!/usr/bin/env python3
"""Build Augur prompt context fragments from agent-owned manifests and files."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build Augur prompt context fragments")
    parser.add_argument("--bundle-mode", default="evidence-driven", help="Deprecated semantic methodology selector; retained for compatibility")
    parser.add_argument("--analysis-mode", default="", help="analysis mode such as full or incremental")
    return parser.parse_args()


def resolve_bundle_mode(raw: str, analysis_mode: str = "") -> str:
    _ = analysis_mode
    value = str(raw or "evidence-driven").strip().lower()
    if value in {"", "auto", "default"}:
        return "evidence-driven"
    return "evidence-driven"


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8").strip()


def build_bundle_prefix(mode: str) -> str:
    _ = mode
    manifest_path = ROOT / ".generated" / "bundles" / "runtime" / "analyze-selective-v1.json"
    if not manifest_path.exists():
        return ""
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    parts: list[str] = []
    for layer in manifest.get("composition_order") or ["skill_bundle", "memory_bundle", "detector_plan"]:
        if layer == "repo_context":
            continue
        if layer == "memory_bundle":
            continue
        relative = manifest.get(layer)
        if not isinstance(relative, str) or not relative.strip():
            continue
        path = ROOT / relative
        if not path.exists():
            continue
        label = {
            "skill_bundle": "Skill Bundle",
            "memory_bundle": "Memory Bundle",
            "detector_plan": "Detector Plan",
        }.get(layer, layer.replace("_", " ").title())
        text = read_text(path)
        if text:
            parts.append(f"## {label}\n\n{text}")
    return f"{chr(10).join(parts)}\n\n" if parts else ""


def build_mode_guide(analysis_mode: str) -> str:
    mode = str(analysis_mode or "").strip().lower()
    if mode not in {"full", "incremental"}:
        return ""
    path = ROOT / "skills" / "analyze" / "modes" / f"{mode}.md"
    if not path.exists():
        return ""
    title = "Full Mode Guide" if mode == "full" else "Incremental Mode Guide"
    text = read_text(path)
    return f"## {title}\n\n{text}\n\n" if text else ""


def main() -> int:
    args = parse_args()
    payload = {
        "bundle_prefix": build_bundle_prefix(resolve_bundle_mode(args.bundle_mode, args.analysis_mode)),
        "mode_guide": build_mode_guide(args.analysis_mode),
    }
    print(json.dumps(payload))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
