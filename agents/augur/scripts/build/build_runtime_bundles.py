#!/usr/bin/env python3
"""Build deterministic runtime analyze bundle manifests for Augur."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GENERATED = ROOT / '.generated' / 'bundles'
MEMORY_BUNDLES = GENERATED / 'memory'
SKILL_BUNDLES = GENERATED / 'skill'
RUNTIME_BUNDLES = GENERATED / 'runtime'


def build_runtime(title: str, semantic_mode: str, memory_bundle: str) -> dict[str, object]:
    return {
        "title": title,
        "version": "1",
        "mode": "analyze",
        "semantic_mode": semantic_mode,
        "skill_bundle": str((SKILL_BUNDLES / "analyze-core-v1.md").relative_to(ROOT)),
        "memory_bundle": str((MEMORY_BUNDLES / memory_bundle).relative_to(ROOT)),
        "detector_plan": str((GENERATED / "detectors" / "execution-plan.json").relative_to(ROOT)),
        "composition_order": [
            "skill_bundle",
            "memory_bundle",
            "detector_plan",
            "repo_context",
        ],
        "notes": [
            "Do not inline the memory bundle into this runtime artifact.",
            "Compose the final prompt by layering the referenced files in composition_order.",
            "Use selective vs holistic memory as model-tier policy rather than as a change to the skill core.",
        ],
    }


def main() -> int:
    RUNTIME_BUNDLES.mkdir(parents=True, exist_ok=True)
    (RUNTIME_BUNDLES / 'analyze-holistic-v1.json').write_text(
        __import__("json").dumps(build_runtime(
            'Augur Runtime Analyze Bundle — Holistic v1',
            'Full semantic catalog is already resident; do not perform extra concept reads unless you need to inspect exact wording.',
            'analyze-holistic-v1.md',
        ), indent=2) + "\n",
        encoding='utf-8',
    )
    (RUNTIME_BUNDLES / 'analyze-selective-v1.json').write_text(
        __import__("json").dumps(build_runtime(
            'Augur Runtime Analyze Bundle — Selective v1',
            'Only summaries are resident; after detector evidence, read full concept/framework semantics for the highest-value candidates before final interpretation.',
            'analyze-selective-v1.md',
        ), indent=2) + "\n",
        encoding='utf-8',
    )
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
