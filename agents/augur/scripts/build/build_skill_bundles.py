#!/usr/bin/env python3
"""Build stable skill-operation bundles for Augur analyze mode."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SKILL = ROOT / "skills" / "analyze" / "SKILL.md"
BUNDLES = ROOT / ".generated" / "bundles" / "skill"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8").rstrip()


def extract_core_sections() -> str:
    text = read(SKILL)
    anchors = [
        "## Produce `atlas.json`, `stories/`, and `narratives.yaml` using the prepared semantic inputs in the canonical output directory for this run.",
        "## Produce `atlas.json`, `stories/`, and `narratives.yaml` using the prepared semantic inputs for this run.",
        "1. Read startup inputs first.",
    ]
    start = -1
    for anchor in anchors:
        start = text.find(anchor)
        if start != -1:
            break
    if start == -1:
        raise RuntimeError("Failed to locate stable analyze skill sections.")
    return text[start:].rstrip()


def build_mode_reference() -> str:
    return "\n".join([
        "## Mode Resources",
        "",
        "The runtime provides the semantic mode and appends the matching operational guide directly into the prompt for this run.",
        "Treat that guide as already loaded context.",
        "Do not spend tool calls trying to locate or read mode-guide files from disk.",
        "Do not blend full-mode and incremental-mode sequences in the same run.",
    ])


def build_common() -> str:
    return "\n".join([
        "# Augur Analyze Skill Bundle — Core v1",
        "",
        "This is the stable operational bundle for Augur `/analyze`.",
        "It defines execution order, mode handling, deterministic evidence expectations, semantic output obligations, and report rules.",
        "It should change less often than repo context and less often than semantic preload bundles.",
        "",
        "## Cache Role",
        "",
        "- Use this as the stable skill-prefix layer.",
        "- Pair it with a separate memory preload bundle.",
        "- Append repo-specific evidence and run-specific instructions last.",
        "",
        build_mode_reference(),
        "",
        "## Analyze Contract",
        "",
        extract_core_sections(),
        "",
    ]).rstrip() + "\n"


def main() -> int:
    BUNDLES.mkdir(parents=True, exist_ok=True)
    (BUNDLES / "analyze-core-v1.md").write_text(build_common(), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
