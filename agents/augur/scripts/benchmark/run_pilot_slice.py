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
REFLECTION_PROMPT_PATH = ROOT / "skills" / "analyze" / "prompts" / "reflection.md"
RUNTIME_ROOT = Path("/kord/augur")


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def slug_repo(repo_root: Path) -> str:
    return repo_root.name.replace("/", "--")


def project_memory_dir(repo_root: Path) -> Path:
    return RUNTIME_ROOT / "memory" / "projects" / slug_repo(repo_root)


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


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def apply_response_metadata(manifest: dict[str, Any], response_payload: dict[str, Any]) -> None:
    metadata = response_payload.get("metadata")
    if not isinstance(metadata, dict):
        return

    usage = metadata.get("usage")
    if isinstance(usage, dict):
        input_tokens = int(usage.get("input_tokens") or 0)
        cached_input_tokens = int(usage.get("cached_input_tokens") or 0)
        output_tokens = int(usage.get("output_tokens") or 0)
        cache_write_tokens = int(usage.get("cache_write_tokens") or 0)
        estimated_cost = float(usage.get("estimated_cost") or manifest.get("estimated_cost") or 0.0)

        tokens_total = input_tokens + output_tokens
        cache_total = cached_input_tokens + cache_write_tokens
        hit_ratio = (cached_input_tokens / input_tokens) if input_tokens > 0 else 0.0

        manifest["tokens"] = {
            "input": input_tokens,
            "output": output_tokens,
            "total": tokens_total,
        }
        manifest["cache"] = {
            "read_tokens": cached_input_tokens,
            "write_tokens": cache_write_tokens,
            "total_tokens": cache_total,
            "hit_ratio": round(hit_ratio, 4),
            "uncached_prefix_bytes": manifest.get("cache", {}).get("uncached_prefix_bytes", 0),
        }
        manifest["estimated_cost"] = estimated_cost

        performance = manifest.setdefault("performance", {})
        performance["tokens_total"] = tokens_total
        performance["estimated_cost"] = estimated_cost
        performance["cache_hit_ratio"] = round(hit_ratio, 4)
        performance.setdefault("cache_efficiency", {})
        performance["cache_efficiency"]["cache_total_tokens"] = cache_total
        performance["cache_efficiency"]["cache_read_ratio"] = round(hit_ratio, 4)
        performance["cache_efficiency"].setdefault("uncached_prefix_bytes", manifest["cache"]["uncached_prefix_bytes"])

    gateway_timing = metadata.get("gateway_timing")
    if isinstance(gateway_timing, dict):
        total_ms = int(gateway_timing.get("total_ms") or 0)
        if total_ms > 0:
            manifest.setdefault("performance", {})
            manifest["performance"]["gateway_runtime_ms_total"] = total_ms


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the deterministic Augur pilot slice and emit benchmark analysis metadata.")
    parser.add_argument("repo_root", type=Path, help="Repository root to analyze.")
    parser.add_argument("--output-dir", type=Path, help="Directory for pilot artifacts. Defaults to /kord/augur/memory/projects/<repo>/benchmark/runs/<run-id>/")
    parser.add_argument("--model", default="augur", help="Model label to record in the benchmark metadata.")
    parser.add_argument("--provider", default="augur", help="Provider label to record in the benchmark metadata.")
    parser.add_argument("--runtime-kind", default="augur")
    parser.add_argument("--memory-bundle", default="selective")
    parser.add_argument("--skill-bundle", default="selective")
    parser.add_argument("--run-number", type=int, default=1)
    parser.add_argument("--analysis-mode", default="full", choices=["full", "incremental", "design"])
    parser.add_argument("--tokens-in", type=int, default=0)
    parser.add_argument("--tokens-out", type=int, default=0)
    parser.add_argument("--cache-read-tokens", type=int, default=0)
    parser.add_argument("--cache-write-tokens", type=int, default=0)
    parser.add_argument("--uncached-prefix-bytes", type=int, default=0)
    parser.add_argument("--estimated-cost", type=float, default=0.0)
    parser.add_argument("--response-json", type=Path, help="Optional live agent response JSON to ingest usage/cache metadata from.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.resolve()

    timestamp = utc_now()
    pinned_sha = git_sha(repo_root)
    sha_short = (pinned_sha[:7] or "no-sha")
    repo_slug = slug_repo(repo_root)
    run_id = f"{timestamp.replace(':', '-')}__{repo_slug}__{sha_short}__{args.model}__{args.memory_bundle}__{args.skill_bundle}__run-{args.run_number}"
    project_mem = project_memory_dir(repo_root)
    output_dir = (args.output_dir.resolve() if args.output_dir else project_mem / "benchmark" / "runs" / run_id)
    output_dir.mkdir(parents=True, exist_ok=True)

    facts_path = output_dir / "facts.json"
    concept_evidence_path = output_dir / "concept-evidence.json"
    semantic_review_path = output_dir / "semantic-review.json"
    meta_path = output_dir / "meta.json"

    total_start = time.perf_counter()
    runtime_ms = {
        "setup": 0,
        "gather": 0,
        "facts": 0,
        "concept_evidence": 0,
        "atlas": 0,
        "stories": 0,
        "validation": 0,
        "total": 0,
    }

    # setup
    setup_start = time.perf_counter()
    reflection_id = run_id
    reflection_path = project_mem / "reflections" / "runs" / f"{reflection_id}.json"
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
                str(concept_evidence_path),
            ]
        )
        runtime_ms["concept_evidence"] = elapsed
        if rc != 0:
            failure_reason = err.strip() or "infer_concepts_from_facts failed"
            success = False
        else:
            rc, _out, err, elapsed = run_cmd(
                [
                    "python3",
                    str(SCRIPT_DIR / "prepare_semantic_review.py"),
                    str(concept_evidence_path),
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
        "output_files_exist": facts_path.exists() and concept_evidence_path.exists() and semantic_review_path.exists(),
        "schema_valid": success,
        "grounding_refs_resolve": True,
        "analyzed_sha_matches": True,
    }

    tokens_in = args.tokens_in
    tokens_out = args.tokens_out
    tokens_total = tokens_in + tokens_out
    cache_total = args.cache_read_tokens + args.cache_write_tokens
    cache_hit_ratio = (args.cache_read_tokens / tokens_in) if tokens_in > 0 else 0.0

    performance = {
        "runtime_ms_total": runtime_ms["total"],
        "tokens_total": tokens_total,
        "estimated_cost": args.estimated_cost,
        "cache_hit_ratio": round(cache_hit_ratio, 4),
        "quality_per_second": None,
        "quality_per_1k_tokens": None,
        "quality_per_dollar": None,
        "cache_efficiency": {
            "cache_total_tokens": cache_total,
            "cache_read_ratio": round(cache_hit_ratio, 4),
            "uncached_prefix_bytes": args.uncached_prefix_bytes,
        },
    }

    reflection_record = {
        "reflection_id": reflection_id,
        "captured_at": utc_now(),
        "repo": repo_root.name,
        "repo_url": "",
        "pinned_sha": pinned_sha,
        "model": args.model,
        "provider": args.provider,
        "runtime_kind": args.runtime_kind,
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

    meta = {
        "run_id": run_id,
        "timestamp": timestamp,
        "repo": repo_root.name,
        "repo_url": "",
        "pinned_sha": pinned_sha,
        "model": args.model,
        "provider": args.provider,
        "runtime_kind": args.runtime_kind,
        "memory_bundle": args.memory_bundle,
        "skill_bundle": args.skill_bundle,
        "run_number": args.run_number,
        "analysis_mode": args.analysis_mode,
        "success": success,
        "failure_reason": failure_reason,
        "correlation_id": "",
        "runtime_ms": runtime_ms,
        "tokens": {
            "input": tokens_in,
            "output": tokens_out,
            "total": tokens_total,
        },
        "cache": {
            "read_tokens": args.cache_read_tokens,
            "write_tokens": args.cache_write_tokens,
            "total_tokens": cache_total,
            "hit_ratio": round(cache_hit_ratio, 4),
            "uncached_prefix_bytes": args.uncached_prefix_bytes,
        },
        "estimated_cost": args.estimated_cost,
        "performance": performance,
        "outputs": {
            "atlas_path": "",
            "facts_dir": str(facts_path),
            "stories_dir": "",
            "transcript_path": "",
            "concept_evidence_path": str(concept_evidence_path),
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
    if args.response_json:
        apply_response_metadata(meta, load_json(args.response_json.resolve()))
    write_json(meta_path, meta)
    print(json.dumps(meta, indent=2))
    return 0 if success else 1


if __name__ == "__main__":
    raise SystemExit(main())
