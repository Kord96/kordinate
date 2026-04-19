#!/usr/bin/env python3
"""Prepare a local Codex prompt pack for Augur semantic analysis."""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPOS_ROOT = Path("/kord/repos")
REPO_ROOT_CANDIDATES = [
    Path("/kord/repos"),
    Path("/kord/shared/repos"),
]
AGENT_ROOT_CANDIDATES = [
    Path("/kord/agents"),
    Path("/kord/shared/agents"),
]
LOCAL_AGENT_HOME = Path("/kord/agents/augur-local-codex")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Prepare a local Codex prompt pack for Augur analyze")
    parser.add_argument("--project", required=True, help="Project name such as fastapi")
    parser.add_argument("--run-dir", help="Prepared analysis run dir to use")
    parser.add_argument("--working-dir", help="Repo root for the analyzed project")
    parser.add_argument("--analysis-mode", default="auto", choices=["auto", "full", "incremental"], help="Prepared semantic analysis mode or auto")
    parser.add_argument("--bundle-mode", default="auto", help="Bundle mode such as evidence-driven or auto")
    parser.add_argument("--pack-dir", help="Output directory for the generated pack")
    return parser.parse_args()


def find_latest_run(project: str) -> Path:
    candidates: list[Path] = []
    for agents_root in AGENT_ROOT_CANDIDATES:
        if not agents_root.exists():
            continue
        for agent_dir in agents_root.glob("*"):
            candidate_root = agent_dir / "memory" / "projects" / project / "analysis"
            if not candidate_root.exists():
                continue
            for run_dir in candidate_root.iterdir():
                if not run_dir.is_dir():
                    continue
                if (run_dir / "blast.json").exists() and (run_dir / "facts" / "startup.json").exists():
                    candidates.append(run_dir)
    if not candidates:
        raise FileNotFoundError(project)
    return max(candidates, key=lambda path: path.stat().st_mtime)


def bootstrap_local_run(project: str, working_dir: Path, analysis_mode: str) -> Path:
    LOCAL_AGENT_HOME.mkdir(parents=True, exist_ok=True)
    prepared = subprocess.check_output(
        [
            "python3",
            str(ROOT / "scripts" / "prepare_analysis_dir.py"),
            str(working_dir),
            "--agent-home",
            str(LOCAL_AGENT_HOME),
            "--project",
            project,
        ],
        text=True,
    ).strip()
    payload = json.loads(prepared)
    run_dir = Path(payload["RUN"]).resolve()
    subprocess.check_call([
        "python3",
        str(ROOT / "scripts" / "prepare_deterministic_run.py"),
        str(working_dir),
        "--run-dir",
        str(run_dir),
        "--project",
        project,
        "--agent-home",
        str(LOCAL_AGENT_HOME),
        "--analysis-mode",
        analysis_mode,
        "--pretty",
    ])
    return run_dir


def run_json(script: Path, *args: str) -> dict:
    payload = subprocess.check_output(
        ["python3", str(script), *args],
        text=True,
    ).strip()
    return json.loads(payload)


def resolve_analysis_plan(project: str, working_dir: Path, analysis_mode: str, bundle_mode: str) -> dict:
    return run_json(
        ROOT / "scripts" / "resolve_analysis_plan.py",
        str(working_dir),
        "--project",
        project,
        "--agent-home",
        str(LOCAL_AGENT_HOME),
        "--analysis-mode",
        analysis_mode,
        "--bundle-mode",
        bundle_mode,
    )


def render_local_runtime_context(context: dict, bundle_mode: str) -> str:
    lines = [
        "## Local Runtime Context",
        "",
        f"- Working directory: `{context['working_dir']}`",
        f"- Output directory: `{context['run_dir']}`",
        f"- Bundle mode: `{bundle_mode}`",
        "- This local Codex session is standing in for the semantic agent runtime.",
        "- Treat the output directory above as the authoritative home for generated artifacts such as `facts/*`, `atlas.json`, `stories/`, and `narratives.yaml`.",
        "- Do not search for alternate validator, schema, or mirrored-agent paths unless a provided path actually fails.",
        "- Use the tools available in this Codex session directly; do not assume daemon-specific tool names.",
        "",
    ]
    return "\n".join(lines)


def render_startup_guidance(context: dict) -> str:
    starter_files = context.get("starter_files") or []
    lines = [
        "## Startup Guidance",
        "",
        f"Directive: {context['startup_directive']}",
        "Starter artifacts:",
        *[f"- `{path}`" for path in starter_files],
        "",
    ]
    return "\n".join(lines)


def build_prompt(project: str, analysis_mode: str, bundle_mode: str, prompt_context: dict, analysis_context: dict) -> str:
    prompt_parts = [
        "You are Augur. Favor design-level reasoning and architecture trade-offs.",
        "",
        (prompt_context.get("bundle_prefix") or "").rstrip(),
        (prompt_context.get("bundle_mode_guide") or "").rstrip(),
        render_local_runtime_context(analysis_context, bundle_mode).rstrip(),
        render_startup_guidance(analysis_context).rstrip(),
        (prompt_context.get("mode_guide") or "").rstrip(),
        f"User request: /analyze {project} --{analysis_mode}",
        "",
    ]
    return "\n".join(part for part in prompt_parts if part)


def main() -> int:
    args = parse_args()
    if args.working_dir:
        working_dir = Path(args.working_dir).resolve()
    else:
        working_dir = next((root / args.project for root in REPO_ROOT_CANDIDATES if (root / args.project).exists()), (REPOS_ROOT / args.project))
        working_dir = working_dir.resolve()
    if not working_dir.exists():
        searched = ", ".join(str(root / args.project) for root in REPO_ROOT_CANDIDATES)
        raise SystemExit(f"working dir not found; searched: {searched}")
    plan = resolve_analysis_plan(args.project, working_dir, args.analysis_mode, args.bundle_mode)
    resolved_analysis_mode = str(plan.get("analysis_mode") or "full")
    resolved_bundle_mode = str(plan.get("bundle_mode") or "evidence-driven")
    if args.run_dir:
        run_dir = Path(args.run_dir).resolve()
    else:
        try:
            run_dir = find_latest_run(args.project).resolve()
        except FileNotFoundError:
            run_dir = bootstrap_local_run(args.project, working_dir, resolved_analysis_mode)

    prompt_context = run_json(
        ROOT / "scripts" / "build_prompt_context.py",
        "--bundle-mode", resolved_bundle_mode,
        "--analysis-mode", resolved_analysis_mode,
    )
    analysis_context = run_json(
        ROOT / "scripts" / "build_analysis_context.py",
        "--project", args.project,
        "--working-dir", str(working_dir),
        "--run-dir", str(run_dir),
        "--analysis-mode", resolved_analysis_mode,
    )

    pack_dir = Path(args.pack_dir).resolve() if args.pack_dir else (run_dir / "local-codex-pack")
    pack_dir.mkdir(parents=True, exist_ok=True)

    prompt_path = pack_dir / "PROMPT.md"
    pack_json_path = pack_dir / "PACK.json"
    readme_path = pack_dir / "README.md"

    prompt_text = build_prompt(args.project, resolved_analysis_mode, resolved_bundle_mode, prompt_context, analysis_context)
    prompt_path.write_text(prompt_text, encoding="utf-8")

    pack = {
        "project": args.project,
        "analysis_mode": resolved_analysis_mode,
        "bundle_mode": resolved_bundle_mode,
        "analysis_plan": plan,
        "working_dir": str(working_dir),
        "run_dir": str(run_dir),
        "analysis_dir": analysis_context["analysis_dir"],
        "prompt_path": str(prompt_path),
        "prompt_context": prompt_context,
        "analysis_context": analysis_context,
        "validator": str(ROOT / "skills" / "analyze" / "scripts" / "validate_output.py"),
    }
    pack_json_path.write_text(json.dumps(pack, indent=2), encoding="utf-8")

    readme_path.write_text(
        "\n".join([
            "# Local Codex Analyze Pack",
            "",
            f"Use the `augur-local-analyze` skill against this pack:",
            f"- pack: `{pack_json_path}`",
            f"- prompt: `{prompt_path}`",
            "",
            "The local Codex session should read PACK.json first, then PROMPT.md, then execute the semantic phase into the provided run dir.",
            "",
        ]),
        encoding="utf-8",
    )

    print(json.dumps({
        "pack_dir": str(pack_dir),
        "pack_json": str(pack_json_path),
        "prompt_path": str(prompt_path),
        "run_dir": str(run_dir),
        "working_dir": str(working_dir),
    }))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
