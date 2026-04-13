#!/usr/bin/env python3
"""Build stable skill-operation bundles for Augur analyze mode."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "analyze" / "SKILL.md"
BUNDLES = ROOT / ".generated" / "bundles" / "skill"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8").rstrip()


def extract_core_sections() -> str:
    text = read(SKILL)
    start = text.find("Produce `atlas.json`, `stories/`, and `narratives.yaml` using the prepared semantic inputs for this run.")
    end = text.find("## Report")
    if start == -1 or end == -1:
        raise RuntimeError("Failed to locate stable analyze skill sections.")
    return text[start:end].rstrip()


def build_mode_reference() -> str:
    return "\n".join([
        "## Mode Resources",
        "",
        "The runtime provides the semantic mode and appends the matching operational guide dynamically.",
        "Use exactly one of:",
        "- `$KORDINATE_HOME/agents/augur/skills/analyze/full-mode.md`",
        "- `$KORDINATE_HOME/agents/augur/skills/analyze/incremental-mode.md`",
        "",
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
