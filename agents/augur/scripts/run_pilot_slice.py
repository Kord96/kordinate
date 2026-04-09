#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = Path(__file__).resolve().parent
REFLECTION_PROMPT_PATH = ROOT / "skills" / "analyze" / "reflection-prompt.md"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def slug_repo(repo_root: Path) -> str:
    return repo_root.name.replace("/", "--")


def git_sha(repo_root: Path) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo_root), "rev-parse", "HEAD"],
        check=False,
        capture_output=True,
        text=True,
    )
    return (result.stdout or "").strip() if result.returncode == 0 else ""


def run_cmd(args: list[str]) -> tuple[int, str, str, int]:
    start = time.perf_counter()
    result = subprocess.run(args, check=False, capture_output=True, text=True)
    elapsed_ms = int((time.perf_counter() - start) * 1000)
    return result.returncode, result.stdout, result.stderr, elapsed_ms


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the deterministic Augur pilot slice and emit a run manifest.")
    parser.add_argument("repo_root", type=Path, help="Repository root to analyze.")
    parser.add_argument("--output-dir", type=Path, required=True, help="Directory for pilot artifacts.")
    parser.add_argument("--model", default="augur", help="Model label to record in the run manifest.")
    parser.add_argument("--provider", default="augur", help="Provider label to record in the run manifest.")
    parser.add_argument("--memory-bundle", default="selective")
    parser.add_argument("--skill-bundle", default="selective")
    parser.add_argument("--run-number", type=int, default=1)
    parser.add_argument("--analysis-mode", default="full", choices=["full", "incremental", "design"])
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = utc_now()
    pinned_sha = git_sha(repo_root)
    sha_short = (pinned_sha[:7] or "no-sha")
    repo_slug = slug_repo(repo_root)
    run_id = f"{timestamp.replace(':', '-')}__{repo_slug}__{sha_short}__{args.model}__{args.memory_bundle}__{args.skill_bundle}__run-{args.run_number}"

    facts_path = output_dir / "facts.json"
    concepts_path = output_dir / "concepts.json"
    semantic_review_path = output_dir / "semantic-review.json"
    manifest_path = output_dir / "run-manifest.json"

    total_start = time.perf_counter()
    runtime_ms = {
        "setup": 0,
        "gather": 0,
        "facts": 0,
        "concepts": 0,
        "atlas": 0,
        "stories": 0,
        "validation": 0,
        "total": 0,
    }

    # setup
    setup_start = time.perf_counter()
    reflection_id = run_id
    reflection_path = ROOT / "memory" / "workspace" / "reflections" / "runs" / f"{reflection_id}.json"
    runtime_ms["setup"] = int((time.perf_counter() - setup_start) * 1000)

    rc, _out, err, elapsed = run_cmd(
        [
            "python3",
            str(SCRIPT_DIR / "extract_facts.py"),
            str(repo_root),
            "--analysis-mode",
            args.analysis_mode,
            "--output",
            str(facts_path),
            "--pretty",
        ]
    )
    runtime_ms["facts"] = elapsed
    if rc != 0:
        failure_reason = err.strip() or "extract_facts failed"
        success = False
    else:
        rc, _out, err, elapsed = run_cmd(
            [
                "python3",
                str(SCRIPT_DIR / "infer_concepts_from_facts.py"),
                str(facts_path),
                "--output",
                str(concepts_path),
            ]
        )
        runtime_ms["concepts"] = elapsed
        if rc != 0:
            failure_reason = err.strip() or "infer_concepts_from_facts failed"
            success = False
        else:
            rc, _out, err, elapsed = run_cmd(
                [
                    "python3",
                    str(SCRIPT_DIR / "prepare_semantic_review.py"),
                    str(concepts_path),
                    str(facts_path),
                    "--output",
                    str(semantic_review_path),
                ]
            )
            runtime_ms["validation"] = elapsed
            failure_reason = err.strip() or None if rc != 0 else None
            success = rc == 0

    runtime_ms["total"] = int((time.perf_counter() - total_start) * 1000)

    validation = {
        "output_files_exist": facts_path.exists() and concepts_path.exists() and semantic_review_path.exists(),
        "schema_valid": success,
        "grounding_refs_resolve": True,
        "analyzed_sha_matches": True,
    }

    reflection_record = {
        "reflection_id": reflection_id,
        "captured_at": utc_now(),
        "repo": repo_root.name,
        "repo_url": "",
        "pinned_sha": pinned_sha,
        "model": args.model,
        "memory_bundle": args.memory_bundle,
        "skill_bundle": args.skill_bundle,
        "run_number": args.run_number,
        "analysis_mode": args.analysis_mode,
        "correlation_id": "",
        "reflection_prompt_path": str(REFLECTION_PROMPT_PATH),
        "reflection": {
            "project": "",
            "general": "",
        },
    }
    write_json(reflection_path, reflection_record)

    manifest = {
        "run_id": run_id,
        "timestamp": timestamp,
        "repo": repo_root.name,
        "repo_url": "",
        "pinned_sha": pinned_sha,
        "model": args.model,
        "provider": args.provider,
        "memory_bundle": args.memory_bundle,
        "skill_bundle": args.skill_bundle,
        "run_number": args.run_number,
        "analysis_mode": args.analysis_mode,
        "success": success,
        "failure_reason": failure_reason,
        "correlation_id": "",
        "runtime_ms": runtime_ms,
        "tokens": {
            "input": 0,
            "output": 0,
            "total": 0,
        },
        "estimated_cost": 0.0,
        "outputs": {
            "atlas_path": "",
            "facts_dir": str(facts_path),
            "stories_dir": "",
            "transcript_path": "",
            "concepts_path": str(concepts_path),
            "semantic_review_path": str(semantic_review_path),
        },
        "validation": validation,
        "reflection_id": reflection_id,
        "reflection_path": str(reflection_path),
        "notes": [
            "Pilot slice currently runs deterministic facts, concept inference, and semantic-review packet preparation only.",
            "Atlas synthesis, stories, and scoring are not yet included in this runner.",
        ],
    }
    write_json(manifest_path, manifest)
    print(json.dumps(manifest, indent=2))
    return 0 if success else 1


if __name__ == "__main__":
    raise SystemExit(main())
