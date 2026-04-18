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
    repair_log = f"{args.target_dir}/repair-log.json"
    prompt = "\n".join([
        f"Validation did not complete cleanly for `{args.target_dir}`.",
        "You must fix the generated output in place and obtain a clean validation result before finishing.",
        f"Validator: `{args.validator_script}`",
        f"Attempt {args.attempt} of {args.max_attempts}.",
        "",
        "Current validator findings:",
        "\n".join(lines) if lines else "- Validation failed with no structured findings.",
        "",
        f"Read `{repair_log}` and use the latest iteration as the authoritative structured repair record.",
        "If the latest repair-log iteration status is `needs_refinement`, the output is structurally valid but not yet quality-clean enough to stop.",
        "Prioritize issues whose status is `open` or `regressed`.",
        "When grounding or naming issues remain, use `facts/symbols-seed.json` when present to replace vague mechanism names with exact identifiers from the prepared high-signal files.",
        "When state grounding issues remain, use `facts/state-seeds.json` when present to replace abstract store wording with exact structs, enums, maps, config variants, or storage selector names from the grounded files.",
        "When framework interpretation is part of the issue, consult `facts/frameworks.json` first. If needed, read only `$KORDINATE_HOME/agents/augur/memory/catalog/frameworks/<framework>/framework.md` and `$KORDINATE_HOME/agents/augur/memory/catalog/frameworks/<framework>/semantics.yaml` for the specific framework in question.",
        "When concept issues remain, consult `facts/concept-evidence.json` first. Use detector backing, contradictions, and semantic questions to decide whether each concept should be strengthened, downgraded to tentative wording, or removed.",
        "If a concept still matters after reviewing `facts/concept-evidence.json`, read only `$KORDINATE_HOME/agents/augur/memory/catalog/concepts/<concept>.md` and, when needed, `$KORDINATE_HOME/agents/augur/detectors/facts/concept-evidence/<concept>/meta.yaml` for that specific concept.",
        "When concept issues remain, make `atlas.json.concepts` repo-specific: explain how the concept manifests here, why it matters architecturally, and link it to concrete components, flows, state, and evidence.",
        "Do not keep a broad concept label just because a detector suggested it. Prefer accepted, well-grounded concepts over a longer pattern list.",
        "When decomposition or narrative-selection issues remain, use `facts/component-seeds.json` and `facts/story-seeds.json` when present to challenge root choice and draft more concern-focused children before editing stories.",
        "When system-overview or other narrative-selection issues remain, use `facts/narrative-seeds.json` when present to challenge which roots, child stories, flow-bearing stories, and boundary stories actually deserve inclusion in the repo overview.",
        "When the repo overview lacks a strong operating model, use `facts/control-hotspots.json` when present to prefer a story that teaches a defining control, request, or execution path.",
        "When the repo overview lacks a real state or dependency boundary, use `facts/state-access-summary.json` when present to prefer a story that explains a concrete storage, state, or external-boundary interaction.",
        "When health modeling issues remain, use `facts/health-candidates.json` when present to distinguish local failures, seam failures, and downstream degraded modes instead of collapsing everything into one flat failure list.",
        "When a boundary failure is modeled but no downstream blast radius or containment is clear, use `facts/health-candidates.json`, `facts/state-access-summary.json`, and `facts/control-hotspots.json` to decide whether to add a propagation scenario or explicitly state containment.",
        "When a narrative overview is too thin, rewrite `system-overview.description` as a compact repo overview that teaches system shape plus the operating model instead of a generic one-liner or component catalog.",
        "When narrative coherence issues remain, rewrite the narrative's `teaches` goals and make sure each included story clearly contributes to one or more of those learning outcomes.",
        "When narrative-count or transition-coherence issues remain, reduce redundant narratives and rewrite per-story bridge text so each transition states why the next story follows from the previous one.",
        "When narrative throughline issues remain, rewrite `throughline` so it explains the teaching arc that connects the selected stories into one lesson.",
        "For narrative fixes, prefer pruning or swapping weak stories over adding more prose. Keep deterministic seeds as constraints and ranking hints, not as a script to restate literally.",
        "Repair the output files now. Do not restart analysis. Keep the same project understanding and only change what is needed to pass validation.",
        f"Do not call `/validate-output` as a shell command. If you need to validate manually inside the runtime, run `python3 {args.validator_script} {args.target_dir}`.",
        "Re-read the canonical schema files and fix the output to match them exactly:",
        "- `$KORDINATE_HOME/agents/augur/schemas/atlas-schema.md`",
        "- `$KORDINATE_HOME/agents/augur/schemas/story-schema.md`",
        "- `$KORDINATE_HOME/agents/augur/schemas/narratives-schema.md`",
    ])
    print(prompt)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
