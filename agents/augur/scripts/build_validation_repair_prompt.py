#!/usr/bin/env python3
"""Render Augur validation repair prompts from agent-owned policy."""

from __future__ import annotations

import argparse
import json


CANONICAL_NARRATIVE_IDS = [
    "system-overview",
    "runtime-paths",
    "state-and-data",
    "integrations",
    "operations-and-failure",
    "extensibility",
    "security-and-access",
]


def relevant_fact_files(findings: list[str]) -> list[str]:
    joined = "\n".join(str(item) for item in findings).lower()
    selected: list[str] = []

    def add(*paths: str) -> None:
        for path in paths:
            if path not in selected:
                selected.append(path)

    if any(token in joined for token in ("grounding", "exact identifier", "exact name", "weak code-shaped overlap")):
        add("facts/symbols-seed.json")
    if any(token in joined for token in ("state", "store", "cache", "persistence", "truthfulness")):
        add("facts/state-seeds.json", "facts/state-access-summary.json")
    if any(token in joined for token in ("concept", "framework")):
        add("facts/concepts.json", "facts/frameworks.json")
    if any(token in joined for token in ("story", "decomposition", "narrative", "overview", "throughline", "teaches")):
        add("derived/story-seeds.json", "derived/component-seeds.json", "derived/narrative-seeds.json")
    if any(token in joined for token in ("health", "monitoring", "gap", "failure", "scenario", "resilien")):
        add("facts/health-candidates.json", "facts/failure-scenario-candidates.json")
    if any(token in joined for token in ("flow", "handoff", "boundary crossing", "boundary or state handoff", "control hotspot")):
        add("facts/control-hotspots.json", "facts/state-access-summary.json")
    return selected


def repair_actions(findings: list[str]) -> list[str]:
    joined = "\n".join(str(item) for item in findings).lower()
    actions: list[str] = []

    def add(action: str) -> None:
        if action not in actions:
            actions.append(action)

    if "outside the canonical narrative palette" in joined:
        add(
            "Rename every non-canonical narrative id to the closest allowed canonical id. "
            f"Allowed ids: {', '.join(CANONICAL_NARRATIVE_IDS)}. "
            "Use `derived/narrative-seeds.json` to choose the best optional narratives."
        )
    if any(token in joined for token in ("narrative-selection", "reuse almost the same story set", "not strongly justified")):
        add(
            "Make narratives meaningfully distinct. If two narratives reuse most of the same stories, merge them or replace the weaker one. "
            "Prefer the highest-ranked optional narratives from `derived/narrative-seeds.json.recommended_narratives`."
        )
    if any(token in joined for token in ("narrative-coherence", "weak adjacent-story transitions", "throughline")):
        add(
            "Rewrite narrative bridge text and throughlines so each adjacent transition explains the architectural reason for moving to the next story."
        )
    if any(token in joined for token in ("story-quality", "many rationale entries", "decision-first")):
        add(
            "Trim story rationale aggressively. Keep only the few most decision-relevant rationale points instead of long exhaustive lists."
        )
    if any(token in joined for token in ("flow-model", "boundary or state handoff", "boundary crossing")):
        add(
            "Rewrite each cited flow so it clearly shows either a real boundary crossing or a state handoff. "
            "If a flow cannot show one, tighten it or split it into a more meaningful operating flow."
        )
    if any(token in joined for token in ("health-ownership-unclear", "health.criteria")):
        add(
            "Rewrite aggregate component health criteria so they describe the parent capability the component owns, not only leaf mechanics."
        )
    return actions


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build Augur validation repair prompt")
    parser.add_argument("--target-dir", required=True)
    parser.add_argument("--validator-script", required=True)
    parser.add_argument("--attempt", type=int, required=True)
    parser.add_argument("--max-attempts", type=int, required=True)
    parser.add_argument("--findings-json", required=True, help="JSON array of finding strings")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    findings = json.loads(args.findings_json)
    lines = [f"- {line}" for line in findings] if isinstance(findings, list) else []
    fact_files = relevant_fact_files(findings if isinstance(findings, list) else [])
    actions = repair_actions(findings if isinstance(findings, list) else [])
    prompt = "\n".join([
        f"Validation did not complete cleanly for `{args.target_dir}`.",
        "Fix the generated output in place and get the run back to a clean validation result.",
        f"Attempt {args.attempt} of {args.max_attempts}.",
        "",
        "Current validator findings:",
        "\n".join(lines) if lines else "- Validation failed with no structured findings.",
        "",
        "Concrete repair actions for this iteration:",
        "\n".join(f"- {action}" for action in actions) if actions else "- Translate the validator findings into the smallest concrete edits needed to pass validation.",
        "",
        "Use only the current validator findings in this prompt as the authoritative repair input for this iteration.",
        "Repair the output files now. Do not restart analysis. Keep the same project understanding and only change what is needed to pass validation.",
        (
            "If you need deterministic help for these findings, prefer this small targeted fact set first:\n"
            + "\n".join(f"- `{path}`" for path in fact_files)
            if fact_files else
            "Use the prepared facts in the run directory only when the current findings actually require extra deterministic support."
        ),
        "Prefer small targeted edits over broad rewrites. Preserve good existing structure and only change the artifacts implicated by the current findings.",
        "You may invoke the validator yourself during repair and continue iterating until the output is clean.",
        "The daemon/workflow still performs one final authoritative validation pass before sealing the run.",
    ])
    print(prompt)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
