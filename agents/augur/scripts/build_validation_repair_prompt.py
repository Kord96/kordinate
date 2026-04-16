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
        f"Validation failed for `{args.target_dir}`.",
        "You must fix the generated output in place and obtain a validation completion token before finishing.",
        f"Validator: `{args.validator_script}`",
        f"Attempt {args.attempt} of {args.max_attempts}.",
        "",
        "Current validator findings:",
        "\n".join(lines) if lines else "- Validation failed with no structured findings.",
        "",
        "Repair the output files now. Do not restart analysis. Keep the same project understanding and only change what is needed to pass validation.",
        f"Do not call `/validate-output` as a shell command. If you need to validate manually inside the runtime, run `python3 {args.validator_script} {args.target_dir}`.",
        "Re-read the canonical schema files and fix the output to match them exactly:",
        "- `/app/agents/augur/schemas/atlas-schema.md`",
        "- `/app/agents/augur/schemas/story-schema.md`",
        "- `/app/agents/augur/schemas/narratives-schema.md`",
    ])
    print(prompt)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
