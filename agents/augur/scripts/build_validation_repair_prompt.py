#!/usr/bin/env python3
"""Render Augur validation repair prompts from agent-owned policy."""

from __future__ import annotations

import argparse
import json


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
        add("facts/concept-evidence.json", "facts/frameworks.json")
    if any(token in joined for token in ("story", "decomposition", "narrative", "overview", "throughline", "teaches")):
        add("facts/story-seeds.json", "facts/component-seeds.json", "facts/narrative-seeds.json")
    if any(token in joined for token in ("health", "monitoring", "gap", "failure", "scenario", "resilien")):
        add("facts/health-candidates.json", "facts/failure-scenario-candidates.json")
    return selected


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
    prompt = "\n".join([
        f"Validation did not complete cleanly for `{args.target_dir}`.",
        "Fix the generated output in place and get the run back to a clean validation result.",
        f"Attempt {args.attempt} of {args.max_attempts}.",
        "",
        "Current validator findings:",
        "\n".join(lines) if lines else "- Validation failed with no structured findings.",
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
        "Do not invoke the validator yourself during repair. The daemon/workflow will rerun validation after your changes.",
    ])
    print(prompt)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
