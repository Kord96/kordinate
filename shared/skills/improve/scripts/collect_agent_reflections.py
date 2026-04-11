#!/usr/bin/env python3
from __future__ import annotations

import argparse
import collections
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import urllib.request


PROJECTS_ROOT = Path("/kord/augur/memory/projects")
DEFAULT_BASE_URL = os.environ.get("KORD_API_URL", os.environ.get("KORD_GATEWAY_URL", "http://kord-api.kord.svc.cluster.local:9091"))
DEFAULT_API_KEY = os.environ.get("KORD_API_KEY", "")


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def fetch_json(url: str, headers: dict[str, str]) -> Any:
    request = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(request) as response:
        return json.loads(response.read().decode("utf-8"))


def post_json(url: str, payload: dict[str, Any], headers: dict[str, str]) -> Any:
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"content-type": "application/json", **headers},
        method="POST",
    )
    with urllib.request.urlopen(request) as response:
        return json.loads(response.read().decode("utf-8"))


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def discover_agents(gateway_url: str, api_key: str) -> dict[str, dict[str, str]]:
    headers = {"x-api-key": api_key} if api_key else {}
    payload = fetch_json(f"{gateway_url.rstrip('/')}/agents?view=variants", headers)
    agents = payload.get("agents", []) if isinstance(payload, dict) else []
    records: dict[str, dict[str, str]] = {}
    for item in agents:
        if not isinstance(item, dict):
            continue
        name = item.get("name")
        provider = item.get("backend_provider")
        model = item.get("backend_model")
        runtime_kind = item.get("runtime")
        if not all(isinstance(value, str) for value in (name, provider, model, runtime_kind)):
            continue
        records[name] = {"provider": provider, "model": model, "runtime_kind": runtime_kind}
    return records


def latest_run_dir(project_dir: Path) -> Path:
    runs = sorted((project_dir / "benchmark" / "runs").iterdir())
    if not runs:
        raise FileNotFoundError(f"no benchmark runs found under {project_dir}")
    return runs[-1]


def build_prompt(run_dir: Path) -> str:
    manifest = load_json(run_dir / "run-manifest.json")
    facts = load_json(run_dir / "facts.json")
    concepts = load_json(run_dir / "concepts.json")
    review = load_json(run_dir / "semantic-review.json")

    domain_counts = collections.Counter(f["domain"] for f in facts.get("facts", []))
    patterns = [c["id"] for c in concepts.get("concepts", {}).get("detected_patterns", [])[:10]]
    candidates = [c["concept"] for c in review.get("candidates", [])[:10]]
    grounded_files = []
    for candidate in review.get("candidates", [])[:3]:
        grounded_files.extend(candidate.get("grounded_in", [])[:4])

    return (
        'Return strict JSON only with exactly these keys: {"project":"...","general":"..."}\n\n'
        f'You are reviewing Augur analyze artifacts for repo {manifest["repo"]} at pinned sha {manifest["pinned_sha"][:7]}.\n\n'
        "Use this context only:\n"
        f"- Top fact domains: {domain_counts.most_common(8)}\n"
        f"- Detected patterns: {patterns}\n"
        f"- Semantic review candidates: {candidates}\n"
        f"- Example grounded files: {grounded_files}\n\n"
        "Write project as repo-specific architectural lessons and misleading signals.\n"
        "Write general as transferable detector/question improvements for Augur.\n"
        "Rules: strict JSON only, plain strings, no markdown, no timing/token talk, under 140 words each.\n"
    )


def extract_reflection_payload(text: str) -> dict[str, str]:
    outer = json.loads(text)
    payload = outer.get("output", text)
    if isinstance(payload, str):
        return json.loads(payload)
    if isinstance(payload, dict):
        return payload
    raise ValueError("unexpected response payload")


def collect_for(agent: str, run_dir: Path, prompt: str, discovered: dict[str, dict[str, str]], gateway_url: str, api_key: str, wait_ms: int) -> Path:
    manifest = load_json(run_dir / "run-manifest.json")
    repo = manifest["repo"]
    pinned_sha = manifest["pinned_sha"]
    sha_short = (pinned_sha[:7] or "no-sha")
    model_info = discovered[agent]
    timestamp = utc_now().replace(":", "-")
    reflection_id = f"{timestamp}__{repo}__{sha_short}__{model_info['model']}__{manifest['memory_bundle']}__{manifest['skill_bundle']}__run-1"
    reflection_path = PROJECTS_ROOT / repo / "reflections" / "runs" / f"{reflection_id}.json"

    headers = {"x-api-key": api_key} if api_key else {}
    response = post_json(
        f"{gateway_url.rstrip('/')}/agents/{agent}/prompt",
        {"prompt": prompt, "timeout_ms": wait_ms},
        headers,
    )
    reflection = extract_reflection_payload(json.dumps(response))
    record = {
        "reflection_id": reflection_id,
        "captured_at": utc_now(),
        "repo": repo,
        "repo_url": manifest.get("repo_url", ""),
        "pinned_sha": pinned_sha,
        "model": model_info["model"],
        "provider": model_info["provider"],
        "runtime_kind": model_info["runtime_kind"],
        "memory_bundle": manifest["memory_bundle"],
        "skill_bundle": manifest["skill_bundle"],
        "run_number": 1,
        "analysis_mode": manifest["analysis_mode"],
        "correlation_id": "",
        "reflection_prompt_path": "agents/augur/skills/analyze/reflection-prompt.md",
        "source_run_manifest_path": str(run_dir / "run-manifest.json"),
        "source_agent": agent,
        "reflection": {
            "project": reflection.get("project", ""),
            "general": reflection.get("general", ""),
        },
    }
    write_json(reflection_path, record)
    return reflection_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Collect external-model reflections through the kord API and store them as Augur raw reflection records.")
    parser.add_argument("--repos", nargs="+", required=True, help="Project slugs under /kord/augur/memory/projects.")
    parser.add_argument("--agents", nargs="+", required=True, help="kord agent names to query.")
    parser.add_argument("--wait-ms", type=int, default=180000)
    parser.add_argument("--gateway-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--api-key", default=DEFAULT_API_KEY)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    discovered = discover_agents(args.gateway_url, args.api_key)
    written: list[str] = []
    failures: list[dict[str, str]] = []
    for repo in args.repos:
        run_dir = latest_run_dir(PROJECTS_ROOT / repo)
        prompt = build_prompt(run_dir)
        for agent in args.agents:
            if agent not in discovered:
                raise SystemExit(f"unknown agent: {agent}")
            try:
                path = collect_for(agent, run_dir, prompt, discovered, args.gateway_url, args.api_key, args.wait_ms)
                written.append(str(path))
            except Exception as error:
                failures.append({"repo": repo, "agent": agent, "error": str(error)})
    print(json.dumps({"written": written, "count": len(written), "failures": failures}, indent=2))
    return 0 if written else 1


if __name__ == "__main__":
    raise SystemExit(main())
