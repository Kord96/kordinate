#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


def utc_now() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


PRECHECK_RULES = {
    "uses_schemas": [
        re.compile(r"atlas-schema\.md|story-schema\.md|narratives-schema\.md|log-schema\.md"),
    ],
    "uses_validator": [
        re.compile(r"validate_output\.py|\blog\.json\b|NEEDS_REFINEMENT|latest log status is `valid`|latest log iteration status is `valid`", re.IGNORECASE),
    ],
    "uses_deterministic_facts": [
        re.compile(r"/facts/|facts/index\.json|blast\.json|startup\.json|component-seeds\.json|story-seeds\.json|symbols-seed\.json|state-seeds\.json|concepts\.json|frameworks\.json|boundaries\.json|hot-files\.json"),
    ],
    "uses_augur_skill": [
        re.compile(r"augur-local-analyze|Use the full current Augur policy|PACK\.json|PROMPT\.md"),
    ],
}

POSTCHECK_RULES = {
    "uses_schemas": [
        "/agents/augur/schemas/atlas-schema.md",
        "/agents/augur/schemas/story-schema.md",
        "/agents/augur/schemas/narratives-schema.md",
        "/agents/augur/schemas/log-schema.md",
    ],
    "uses_validator": [
        "/agents/augur/skills/analyze/validator/validate.py",
        "log.json",
    ],
    "uses_deterministic_facts": [
        "/facts/",
        "/blast.json",
        "/startup.json",
        "component-seeds.json",
        "story-seeds.json",
        "symbols-seed.json",
        "state-seeds.json",
        "concepts.json",
    ],
    "uses_augur_skill": [
        "augur-local-analyze",
        "PACK.json",
        "PROMPT.md",
    ],
}


def condition_flags(condition: dict[str, Any]) -> dict[str, bool]:
    return {
        key: bool(condition.get(key, False))
        for key in (
            "uses_schemas",
            "uses_validator",
            "uses_deterministic_facts",
            "uses_augur_skill",
            "uses_semantic_memory",
        )
    }


def preflight_isolation_check(prompt_text: str, flags: dict[str, bool]) -> list[str]:
    failures: list[str] = []
    for key, patterns in PRECHECK_RULES.items():
        if flags.get(key):
            continue
        for pattern in patterns:
            if pattern.search(prompt_text):
                failures.append(f"prompt references forbidden capability {key}: {pattern.pattern}")
    return failures


def postrun_isolation_check(run_dir: Path, flags: dict[str, bool]) -> list[str]:
    stdout_path = run_dir / "stdout.jsonl"
    final_path = run_dir / "final-message.txt"
    haystacks: list[str] = []
    if stdout_path.exists():
        haystacks.append(stdout_path.read_text(encoding="utf-8", errors="ignore"))
    if final_path.exists():
        haystacks.append(final_path.read_text(encoding="utf-8", errors="ignore"))
    combined = "\n".join(haystacks)
    failures: list[str] = []
    for key, needles in POSTCHECK_RULES.items():
        if flags.get(key):
            continue
        for needle in needles:
            if needle in combined:
                failures.append(f"run output mentions forbidden capability {key}: {needle}")
                break
    return failures


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def update_summary_condition(summary: dict[str, Any], result: dict[str, Any]) -> None:
    cid = str(result.get("condition_id") or "")
    for idx, existing in enumerate(summary.get("conditions", [])):
        if str(existing.get("condition_id") or "") == cid:
            summary["conditions"][idx] = result
            return
    summary.setdefault("conditions", []).append(result)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Codex ablation prompts non-interactively from an ablation manifest.")
    parser.add_argument("manifest", type=Path, help="Path to ablation manifest.json")
    parser.add_argument(
        "--condition",
        action="append",
        dest="conditions",
        help="Condition id to run. Repeatable. Defaults to all conditions in the manifest.",
    )
    parser.add_argument("--model", default="", help="Codex model override. Uses CLI default if omitted.")
    parser.add_argument(
        "--runner-output-dir",
        type=Path,
        help="Directory for runner logs and metadata. Defaults to <manifest-dir>/runs/<timestamp>/",
    )
    parser.add_argument("--codex-bin", default="codex", help="Codex executable to invoke.")
    parser.add_argument(
        "--jobs",
        type=int,
        default=1,
        help="Number of conditions to run concurrently. Default: 1 (sequential).",
    )
    parser.add_argument("--dry-run", action="store_true", help="Print planned commands without executing them.")
    return parser.parse_args()


def build_codex_command(
    codex_bin: str,
    repo_root: Path,
    model: str,
    final_message_path: Path,
) -> list[str]:
    cmd = [
        codex_bin,
        "exec",
        "--dangerously-bypass-approvals-and-sandbox",
        "-C",
        str(repo_root),
        "--output-last-message",
        str(final_message_path),
        "--json",
        "-",
    ]
    if model:
        cmd.extend(["-m", model])
    return cmd


def run_condition(
    codex_bin: str,
    repo_root: Path,
    model: str,
    prompt_path: Path,
    run_dir: Path,
    dry_run: bool,
    flags: dict[str, bool],
) -> dict[str, Any]:
    run_dir.mkdir(parents=True, exist_ok=True)
    prompt_text = prompt_path.read_text(encoding="utf-8")
    preflight_failures = preflight_isolation_check(prompt_text, flags)
    final_message_path = run_dir / "final-message.txt"
    stdout_path = run_dir / "stdout.jsonl"
    stderr_path = run_dir / "stderr.log"
    command = build_codex_command(codex_bin, repo_root, model, final_message_path)

    result_payload: dict[str, Any] = {
        "started_at": utc_now(),
        "repo_root": str(repo_root),
        "prompt_path": str(prompt_path),
        "model": model or None,
        "command": command,
        "flags": flags,
        "isolation": {"preflight_failures": preflight_failures, "postrun_failures": [], "status": "failed" if preflight_failures else "pending"},
        "status": "planned" if dry_run else "running",
        "stdout_path": str(stdout_path),
        "stderr_path": str(stderr_path),
        "final_message_path": str(final_message_path),
    }
    write_json(run_dir / "run.json", result_payload)

    if preflight_failures:
        result_payload["completed_at"] = utc_now()
        result_payload["status"] = "failed"
        write_json(run_dir / "run.json", result_payload)
        return result_payload

    if dry_run:
        result_payload["completed_at"] = utc_now()
        result_payload["status"] = "dry-run"
        result_payload["isolation"]["status"] = "not-run"
        write_json(run_dir / "run.json", result_payload)
        return result_payload

    env = os.environ.copy()
    env["AUGUR_PROJECT_ROOT"] = str(repo_root)
    env.setdefault("KORDINATE_HOME", "/kord/workstation/home/project/kordinate")

    start = time.perf_counter()
    completed = subprocess.run(
        command,
        input=prompt_text,
        text=True,
        capture_output=True,
        env=env,
        check=False,
    )
    elapsed_ms = int((time.perf_counter() - start) * 1000)
    stdout_path.write_text(completed.stdout or "", encoding="utf-8")
    stderr_path.write_text(completed.stderr or "", encoding="utf-8")

    postrun_failures = postrun_isolation_check(run_dir, flags)
    result_payload.update(
        {
            "completed_at": utc_now(),
            "status": "ok" if completed.returncode == 0 and not postrun_failures else "failed",
            "returncode": completed.returncode,
            "elapsed_ms": elapsed_ms,
        }
    )
    result_payload["isolation"] = {
        "preflight_failures": preflight_failures,
        "postrun_failures": postrun_failures,
        "status": "passed" if completed.returncode == 0 and not postrun_failures else "failed",
    }
    write_json(run_dir / "run.json", result_payload)
    return result_payload


def main() -> int:
    args = parse_args()
    manifest_path = args.manifest.resolve()
    manifest = load_json(manifest_path)
    manifest_dir = manifest_path.parent
    repo_root = Path(str(manifest["repo"]["repo_root"])).resolve()

    selected_conditions = set(args.conditions or [])
    conditions = []
    for condition in manifest.get("conditions", []):
        cid = str(condition.get("id") or "")
        if selected_conditions and cid not in selected_conditions:
            continue
        conditions.append(condition)

    if not conditions:
        raise SystemExit("no conditions selected")

    run_root = (
        args.runner_output_dir.resolve()
        if args.runner_output_dir
        else (manifest_dir / "runs" / datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ"))
    )
    run_root.mkdir(parents=True, exist_ok=True)

    summary: dict[str, Any] = {
        "started_at": utc_now(),
        "manifest": str(manifest_path),
        "repo_root": str(repo_root),
        "model": args.model or None,
        "jobs": max(1, args.jobs),
        "conditions": [],
    }
    for condition in conditions:
        cid = str(condition["id"])
        prompt_path = (manifest_dir / str(condition["prompt_file"])).resolve()
        summary["conditions"].append(
            {
                "condition_id": cid,
                "prompt_path": str(prompt_path),
                "flags": condition_flags(condition),
                "status": "queued" if not args.dry_run else "planned",
            }
        )
    write_json(run_root / "summary.json", summary)

    if args.dry_run:
        for condition in conditions:
            cid = str(condition["id"])
            prompt_path = (manifest_dir / str(condition["prompt_file"])).resolve()
            condition_run_dir = run_root / cid
            result = run_condition(
                codex_bin=args.codex_bin,
                repo_root=repo_root,
                model=args.model,
                prompt_path=prompt_path,
                run_dir=condition_run_dir,
                dry_run=True,
                flags=condition_flags(condition),
            )
            result["condition_id"] = cid
            update_summary_condition(summary, result)
        summary["completed_at"] = utc_now()
        write_json(run_root / "summary.json", summary)
        return 0

    exit_code = 0
    jobs = max(1, args.jobs)

    def launch(condition: dict[str, Any]) -> tuple[str, dict[str, Any]]:
        cid = str(condition["id"])
        prompt_path = (manifest_dir / str(condition["prompt_file"])).resolve()
        condition_run_dir = run_root / cid
        flags = condition_flags(condition)
        update_summary_condition(
            summary,
            {
                "condition_id": cid,
                "prompt_path": str(prompt_path),
                "flags": flags,
                "status": "running",
                "started_at": utc_now(),
            },
        )
        write_json(run_root / "summary.json", summary)
        result = run_condition(
            codex_bin=args.codex_bin,
            repo_root=repo_root,
            model=args.model,
            prompt_path=prompt_path,
            run_dir=condition_run_dir,
            dry_run=False,
            flags=flags,
        )
        result["condition_id"] = cid
        return cid, result

    with ThreadPoolExecutor(max_workers=jobs) as executor:
        future_map = {executor.submit(launch, condition): str(condition["id"]) for condition in conditions}
        for future in as_completed(future_map):
            cid = future_map[future]
            try:
                _, result = future.result()
            except Exception as exc:  # pragma: no cover
                result = {
                    "condition_id": cid,
                    "started_at": None,
                    "completed_at": utc_now(),
                    "status": "failed",
                    "error": repr(exc),
                }
                exit_code = 1
            else:
                if result.get("status") == "failed":
                    exit_code = 1
            update_summary_condition(summary, result)
            write_json(run_root / "summary.json", summary)

    summary["completed_at"] = utc_now()
    write_json(run_root / "summary.json", summary)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
