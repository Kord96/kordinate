#!/usr/bin/env python3
"""Render Augur validation repair prompts from agent-owned policy."""

from __future__ import annotations

import argparse
import json


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
    prompt = "\n".join([
        f"Validation did not complete cleanly for `{args.target_dir}`.",
        "You must fix the generated output in place and obtain a clean validation result before finishing.",
        f"Attempt {args.attempt} of {args.max_attempts}.",
        "",
        "Current validator findings:",
        "\n".join(lines) if lines else "- Validation failed with no structured findings.",
        "",
        "Use only the current validator findings in this prompt as the authoritative repair input for this iteration.",
        "When grounding or naming issues remain, use `facts/symbols-seed.json` when present to replace vague mechanism names with exact identifiers from the prepared high-signal files.",
        "When state grounding issues remain, use `facts/state-seeds.json` when present to replace abstract store wording with exact structs, enums, maps, config variants, or storage selector names from the grounded files.",
        "When framework interpretation is part of the issue, consult `facts/frameworks.json` first. If needed, start from `$FRAMEWORK_CATALOG_INDEX`, then read only `$AGENT_ROOT/memory/catalog/frameworks/<framework>/framework.md` and `$AGENT_ROOT/memory/catalog/frameworks/<framework>/semantics.yaml` for the specific framework in question.",
        "When concept issues remain, consult `facts/concept-evidence.json` first. Use supporting evidence, counter evidence, evidence gaps, and review questions to decide whether each concept should be strengthened, downgraded to tentative wording, or removed.",
        "If a concept still matters after reviewing `facts/concept-evidence.json`, start from `$CONCEPT_CATALOG_INDEX`, then read only `$AGENT_ROOT/memory/catalog/concepts/<concept>.md` and, when needed, `$AGENT_ROOT/detectors/facts/concept-evidence/<concept>/meta.yaml` for that specific concept.",
        "When concept issues remain, make `atlas.json.concepts` repo-specific: explain how the concept manifests here, why it matters architecturally, and link it to concrete components, flows, state, and evidence.",
        "Do not keep a broad concept label just because a detector suggested it. Prefer accepted, well-grounded concepts over a longer pattern list.",
        "When decomposition or narrative-selection issues remain, use `facts/component-seeds.json` and `facts/story-seeds.json` when present to challenge root choice and draft more concern-focused children before editing stories.",
        "When system-overview or other narrative-selection issues remain, use `facts/narrative-seeds.json` when present to challenge which roots, child stories, flow-bearing stories, and boundary stories actually deserve inclusion in the repo overview.",
        "If optional narratives are disputed, use `recommended_narratives` ranking to decide whether a weaker optional narrative should be replaced by a stronger evidence-backed canonical narrative type.",
        "When narrative-type issues remain, use `facts/narrative-seeds.json` to decide whether a narrative should be kept, renamed to a canonical palette id, merged away, or replaced by a stronger evidence-backed narrative type.",
        "When the repo overview lacks a strong operating model, use `facts/control-hotspots.json` when present to prefer a story that teaches a defining control, request, or execution path.",
        "When the repo overview lacks a real state or dependency boundary, use `facts/state-access-summary.json` when present to prefer a story that explains a concrete storage, state, or external-boundary interaction.",
        "When health modeling issues remain, keep unit `health` minimal: add `health.criteria`, `health.triggers_failure_scenarios`, and `health.participates_in_failure_scenarios`, then move shared cascade details to top-level `failure_scenarios`.",
        "When shared cascades are implicated, use `facts/failure-scenario-candidates.json` to decide whether several unit-level failure notes should become one top-level `failure_scenarios` entry.",
        "When observability issues remain, use `facts/health-candidates.json`, `facts/failure-scenario-candidates.json`, and concept monitoring expectations to build top-level `monitoring` entries grounded in the components, flows, dependencies, or scenarios they cover.",
        "When gap modeling issues remain, move missing monitoring, resilience, concept, or anti-pattern concerns into the top-level `gaps` list with explicit `affects` ids and recommendations.",
        "When health blocks are thin, add `health.criteria` so the component, flow, or dependency states what healthy operation looks like and links to the shared failure scenarios it can trigger or participate in.",
        "Use the atlas component graph while repairing health: parent-child structure tells you ownership, but `depends_on`, shared state, and shared external dependencies should drive failure-scenario links more strongly than simple containment.",
        "When a narrative overview is too thin, rewrite `system-overview.description` as a compact repo overview that teaches system shape plus the operating model instead of a generic one-liner or component catalog.",
        "When narrative coherence issues remain, rewrite the narrative's `teaches` goals and make sure each included story clearly contributes to one or more of those learning outcomes.",
        "When narrative-count or transition-coherence issues remain, reduce redundant narratives and rewrite per-story bridge text so each transition states why the next story follows from the previous one.",
        "When narrative throughline issues remain, rewrite `throughline` so it explains the teaching arc that connects the selected stories into one lesson.",
        "For narrative fixes, prefer pruning or swapping weak stories over adding more prose. Keep deterministic seeds as constraints and ranking hints, not as a script to restate literally.",
        "Repair the output files now. Do not restart analysis. Keep the same project understanding and only change what is needed to pass validation.",
        "Do not invoke the validator yourself during repair. The daemon/workflow will rerun validation after your changes.",
    ])
    print(prompt)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
