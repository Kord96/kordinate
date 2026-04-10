#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

import agent_prompt


DEFAULT_CACHE_TTL_SECONDS = 300
DEFAULT_STATE_DIR = Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex"))) / "state"
DEFAULT_CACHE_PATH = DEFAULT_STATE_DIR / "kord-agent-discovery.json"
DEFAULT_REQUESTS_DIR = DEFAULT_STATE_DIR / "kord-requests"
DEFAULT_AUTH_PATH = agent_prompt.DEFAULT_AUTH_PATH


def load_cached_discovery(cache_path: Path, ttl_seconds: int) -> dict[str, Any] | None:
    if not cache_path.exists():
        return None
    age = time.time() - cache_path.stat().st_mtime
    if age > ttl_seconds:
        return None
    try:
        return json.loads(cache_path.read_text())
    except Exception:
        return None


def save_cached_discovery(cache_path: Path, payload: dict[str, Any]) -> None:
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache_path.write_text(json.dumps(payload, indent=2) + "\n")


def fetch_discovery(args: argparse.Namespace, refresh: bool) -> dict[str, Any]:
    if not refresh and not getattr(args, "verbose", False):
        cached = load_cached_discovery(Path(args.cache_path), args.cache_ttl_seconds)
        if cached is not None:
            return cached

    discovery_args = argparse.Namespace(
        discovery_url=args.discovery_url,
        gateway_url=args.gateway_url,
        api_key=args.api_key,
        agent=None,
        verbose=getattr(args, "verbose", False),
    )
    payload = agent_prompt.discovery_payload(discovery_args)
    if not isinstance(payload, dict):
        raise SystemExit("discovery payload is not an object")
    if not getattr(args, "verbose", False):
        save_cached_discovery(Path(args.cache_path), payload)
    return payload


def agent_records(payload: dict[str, Any]) -> list[dict[str, Any]]:
    agents = payload.get("agents", [])
    return [item for item in agents if isinstance(item, dict) and isinstance(item.get("name"), str)]


def resolve_agent(target: str, payload: dict[str, Any]) -> dict[str, Any]:
    records = agent_records(payload)
    exact = {record["name"]: record for record in records}
    if target in exact:
        return exact[target]

    aliases: dict[str, list[dict[str, Any]]] = {}
    for record in records:
        name = record["name"]
        aliases.setdefault(name, []).append(record)
        if "-" in name:
            suffix = name.split("-", 1)[1]
            aliases.setdefault(suffix, []).append(record)

    matches = aliases.get(target, [])
    if len(matches) == 1:
        return matches[0]
    if len(matches) > 1:
        generic = [item for item in matches if item["name"].startswith("generic-")]
        if len(generic) == 1:
            return generic[0]
        names = ", ".join(sorted(item["name"] for item in matches))
        raise SystemExit(f"agent alias '{target}' is ambiguous: {names}")

    raise SystemExit(f"unknown agent '{target}'")


def list_agents(args: argparse.Namespace) -> int:
    payload = fetch_discovery(args, refresh=args.refresh)
    records = agent_records(payload)
    for record in sorted(records, key=lambda item: item["name"]):
        active = "active" if record.get("active") else "inactive"
        capabilities = "; ".join(record.get("capabilities", []))
        print(f"{record['name']}\t{record.get('backend_provider','?')}\t{record.get('backend_model','?')}\t{active}\t{capabilities}")
    return 0


def show_agents(args: argparse.Namespace) -> int:
    payload = fetch_discovery(args, refresh=args.refresh)
    print(json.dumps(payload, indent=2))
    return 0


def auth_login(args: argparse.Namespace) -> int:
    login_args = argparse.Namespace(
        gateway_url=args.gateway_url,
        api_key=args.api_key,
        auth_path=args.auth_path,
    )
    return agent_prompt.auth_login_command(login_args)


def auth_status(args: argparse.Namespace) -> int:
    return agent_prompt.auth_status_command(argparse.Namespace(auth_path=args.auth_path))


def auth_clear(args: argparse.Namespace) -> int:
    return agent_prompt.auth_clear_command(argparse.Namespace(auth_path=args.auth_path))


def prompt_via_kord(args: argparse.Namespace) -> int:
    payload = fetch_discovery(args, refresh=args.refresh)
    record = resolve_agent(args.target, payload)
    working_dir = args.working_dir or record.get("default_working_dir")
    if args.async_mode:
        if not args.gateway_url:
            raise SystemExit("--async requires KORD_API_URL or --gateway-url")
        headers = {}
        if args.api_key:
            headers["x-api-key"] = args.api_key
        request_payload: dict[str, Any] = {
            "prompt": args.prompt,
            "async": True,
        }
        if working_dir:
            request_payload["working_dir"] = working_dir
        if args.timeout_ms is not None:
            request_payload["timeout_ms"] = args.timeout_ms
        if args.reflect:
            request_payload["reflect"] = True
        if args.reflection_prompt:
            request_payload["reflection_prompt"] = args.reflection_prompt
        if args.session_id:
            request_payload["session_id"] = args.session_id
        response = agent_prompt.post_json(
            f"{args.gateway_url.rstrip('/')}/agents/{record['name']}/prompt",
            request_payload,
            headers,
        )
        if not isinstance(response, dict) or "request_id" not in response:
            print(json.dumps(response, indent=2))
            return 1
        request_id = str(response["request_id"])
        requests_dir = Path(args.requests_dir)
        requests_dir.mkdir(parents=True, exist_ok=True)
        status_path = requests_dir / f"{request_id}.json"
        log_path = requests_dir / f"{request_id}.log"
        status_path.write_text(json.dumps({
            "request_id": request_id,
            "status": "pending",
            "agent": record["name"],
            "submitted_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }, indent=2) + "\n")
        watch_cmd = [
            sys.executable,
            str(Path(agent_prompt.__file__)),
            "watch",
            request_id,
            "--gateway-url", args.gateway_url,
            "--api-key", args.api_key,
            "--wait-ms", str(args.wait_ms),
        ]
        with log_path.open("ab") as log_file, status_path.open("wb") as out_file:
            subprocess.Popen(
                watch_cmd,
                stdout=out_file,
                stderr=log_file,
                start_new_session=True,
            )
        print(json.dumps({
            "request_id": request_id,
            "status": "pending",
            "agent": record["name"],
            "status_path": str(status_path),
            "log_path": str(log_path),
        }, indent=2))
        return 0

    prompt_args = argparse.Namespace(
        agent=record["name"],
        prompt=args.prompt,
        working_dir=working_dir,
        timeout_ms=args.timeout_ms,
        reflect=args.reflect,
        reflection_prompt=args.reflection_prompt,
        session_id=args.session_id,
        discovery_url=args.discovery_url,
        gateway_url=args.gateway_url,
        api_key=args.api_key,
        async_mode=False,
    )
    return agent_prompt.prompt(prompt_args)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Ergonomic kord wrapper for discovery and agent prompting")
    parser.add_argument("--refresh", action="store_true", help="ignore cached discovery and refresh now")
    parser.add_argument("--cache-path", default=str(DEFAULT_CACHE_PATH))
    parser.add_argument("--requests-dir", default=str(DEFAULT_REQUESTS_DIR))
    parser.add_argument("--auth-path", default=str(DEFAULT_AUTH_PATH))
    parser.add_argument("--cache-ttl-seconds", type=int, default=DEFAULT_CACHE_TTL_SECONDS)
    parser.add_argument("--discovery-url", default=agent_prompt.DEFAULT_DISCOVERY_URL)
    parser.add_argument("--gateway-url", default=agent_prompt.DEFAULT_GATEWAY_URL)
    parser.add_argument("--api-key", default=agent_prompt.DEFAULT_API_KEY)
    parser.add_argument("--working-dir")
    parser.add_argument("--timeout-ms", type=int)
    parser.add_argument("--wait-ms", type=int, default=120000)
    parser.add_argument("--async", dest="async_mode", action="store_true")
    parser.add_argument("--session-id", help="Stable session lane for related requests")
    parser.add_argument("--reflect", action="store_true")
    parser.add_argument("--reflection-prompt")
    parser.add_argument("--verbose", action="store_true", help="show verbose discovery details")
    parser.add_argument("target", help="'agents', 'discover', an agent name, or a shorthand alias like 'opus'")
    parser.add_argument("verb", nargs="?", help="use 'on' to prompt an agent")
    parser.add_argument("rest", nargs=argparse.REMAINDER)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.target in {"agents", "list"}:
        return list_agents(args)
    if args.target in {"discover", "show"}:
        return show_agents(args)
    if args.target == "auth":
        if args.verb == "login":
            if not args.rest:
                parser.error("use 'kord auth login <api-key>' or pass --api-key")
            if not args.api_key:
                args.api_key = args.rest[0]
            return auth_login(args)
        if args.verb == "status":
            return auth_status(args)
        if args.verb == "clear":
            return auth_clear(args)
        parser.error("use 'kord auth login <api-key>', 'kord auth status', or 'kord auth clear'")
    if args.verb != "on":
        parser.error("use 'kord <agent> on <prompt...>' or 'kord agents'")

    prompt = " ".join(args.rest).strip()
    if not prompt:
        parser.error("missing prompt after 'on'")
    args.prompt = prompt
    return prompt_via_kord(args)


if __name__ == "__main__":
    raise SystemExit(main())
