#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys
import time
import urllib.request
from typing import Any


DEFAULT_STATE_DIR = Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex"))) / "state"
DEFAULT_AUTH_PATH = DEFAULT_STATE_DIR / "kord-auth.json"
DEFAULT_BASE_URL = "http://kord-api.kord.svc.cluster.local:9091"


def load_auth_state(path: Path = DEFAULT_AUTH_PATH) -> dict[str, str]:
    try:
        payload = json.loads(path.read_text())
    except Exception:
        return {}
    if not isinstance(payload, dict):
        return {}
    return {str(key): str(value) for key, value in payload.items() if isinstance(value, str)}


def save_auth_state(data: dict[str, str], path: Path = DEFAULT_AUTH_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n")
    path.chmod(0o600)


def resolve_default_gateway_url() -> str:
    return os.environ.get("KORD_API_URL", os.environ.get("KORD_GATEWAY_URL", load_auth_state().get("gateway_url", DEFAULT_BASE_URL)))


def resolve_default_api_key() -> str:
    return os.environ.get("KORD_API_KEY", load_auth_state().get("api_key", ""))


DEFAULT_DISCOVERY_URL = resolve_default_gateway_url()
DEFAULT_GATEWAY_URL = resolve_default_gateway_url()
DEFAULT_API_KEY = resolve_default_api_key()


def fetch_json(url: str) -> Any:
    with urllib.request.urlopen(url) as response:
        return json.loads(response.read().decode("utf-8"))


def fetch_json_with_headers(url: str, headers: dict[str, str]) -> Any:
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


def fetch_request_status(gateway_url: str, request_id: str, headers: dict[str, str]) -> Any:
    return fetch_json_with_headers(f"{gateway_url.rstrip('/')}/requests/{request_id}", headers)


def discovery_payload(args: argparse.Namespace) -> Any:
    path = f"/agents/{args.agent}" if getattr(args, "agent", None) else "/agents"
    if getattr(args, "verbose", False):
        sep = "&" if "?" in path else "?"
        path = f"{path}{sep}verbose=1"
    gateway_url = getattr(args, "gateway_url", "") or getattr(args, "discovery_url", "")
    if not gateway_url:
        raise SystemExit("KORD_API_URL or --gateway-url is required for discovery")
    headers = {}
    if getattr(args, "api_key", ""):
        headers["x-api-key"] = args.api_key
    return fetch_json_with_headers(f"{gateway_url.rstrip('/')}{path}", headers)


def discover(args: argparse.Namespace) -> int:
    payload = discovery_payload(args)
    print(json.dumps(payload, indent=2))
    return 0


def prompt(args: argparse.Namespace) -> int:
    gateway_url = getattr(args, "gateway_url", "") or getattr(args, "discovery_url", "")
    if not gateway_url:
        raise SystemExit("KORD_API_URL or --gateway-url is required for prompting")
    payload = {
        "prompt": args.prompt,
    }
    if args.working_dir:
        payload["working_dir"] = args.working_dir
    if args.timeout_ms is not None:
        payload["timeout_ms"] = args.timeout_ms
    if args.reflect:
        payload["reflect"] = True
    if args.reflection_prompt:
        payload["reflection_prompt"] = args.reflection_prompt
    if args.session_id:
        payload["session_id"] = args.session_id
    if getattr(args, "async_mode", False):
        payload["async"] = True
    headers = {}
    if getattr(args, "api_key", ""):
        headers["x-api-key"] = args.api_key
    start = time.time()
    response = post_json(f"{gateway_url.rstrip('/')}/agents/{args.agent}/prompt", payload, headers)
    wall_ms = int((time.time() - start) * 1000)
    if isinstance(response, dict):
        response.setdefault("metadata", {})
        response["metadata"].setdefault("caller_timing", {})
        response["metadata"]["caller_timing"]["wall_ms"] = wall_ms
    print(json.dumps(response, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Discover and prompt daemon-backed agent pods")
    sub = parser.add_subparsers(dest="command", required=True)

    auth_parser = sub.add_parser("auth", help="store or inspect kord API auth state")
    auth_sub = auth_parser.add_subparsers(dest="auth_command", required=True)

    auth_login = auth_sub.add_parser("login", help="store KORD API URL and API key for future calls")
    auth_login.add_argument("--gateway-url", default=DEFAULT_GATEWAY_URL)
    auth_login.add_argument("--api-key", required=True)
    auth_login.add_argument("--auth-path", default=str(DEFAULT_AUTH_PATH))
    auth_login.set_defaults(func=auth_login_command)

    auth_status = auth_sub.add_parser("status", help="show whether auth state is configured")
    auth_status.add_argument("--auth-path", default=str(DEFAULT_AUTH_PATH))
    auth_status.set_defaults(func=auth_status_command)

    auth_clear = auth_sub.add_parser("clear", help="remove stored auth state")
    auth_clear.add_argument("--auth-path", default=str(DEFAULT_AUTH_PATH))
    auth_clear.set_defaults(func=auth_clear_command)

    discover_parser = sub.add_parser("discover", help="return the discovery response")
    discover_parser.add_argument("--discovery-url", default=DEFAULT_DISCOVERY_URL)
    discover_parser.add_argument("--gateway-url", default=DEFAULT_GATEWAY_URL)
    discover_parser.add_argument("--api-key", default=DEFAULT_API_KEY)
    discover_parser.add_argument("--agent")
    discover_parser.add_argument("--verbose", action="store_true")
    discover_parser.set_defaults(func=discover)

    prompt_parser = sub.add_parser("prompt", help="send one request to an agent and wait for a reply")
    prompt_parser.add_argument("agent")
    prompt_parser.add_argument("prompt")
    prompt_parser.add_argument("--working-dir")
    prompt_parser.add_argument("--timeout-ms", type=int)
    prompt_parser.add_argument("--reflect", action="store_true")
    prompt_parser.add_argument("--reflection-prompt")
    prompt_parser.add_argument("--session-id", help="Stable session lane for related requests")
    prompt_parser.add_argument("--async", dest="async_mode", action="store_true")
    prompt_parser.add_argument("--discovery-url", default=DEFAULT_DISCOVERY_URL)
    prompt_parser.add_argument("--gateway-url", default=DEFAULT_GATEWAY_URL)
    prompt_parser.add_argument("--api-key", default=DEFAULT_API_KEY)
    prompt_parser.set_defaults(func=prompt)

    watch_parser = sub.add_parser("watch", help="poll one async request until completion")
    watch_parser.add_argument("request_id")
    watch_parser.add_argument("--gateway-url", default=DEFAULT_GATEWAY_URL)
    watch_parser.add_argument("--api-key", default=DEFAULT_API_KEY)
    watch_parser.add_argument("--wait-ms", type=int, default=120000)
    watch_parser.add_argument("--poll-interval-ms", type=int, default=2000)
    watch_parser.set_defaults(func=watch)

    return parser


def watch(args: argparse.Namespace) -> int:
    if not args.gateway_url:
        raise SystemExit("--gateway-url required for watch")
    headers = {}
    if getattr(args, "api_key", ""):
        headers["x-api-key"] = args.api_key
    deadline = time.time() + (args.wait_ms / 1000.0)
    while time.time() < deadline:
        payload = fetch_request_status(args.gateway_url, args.request_id, headers)
        if isinstance(payload, dict) and payload.get("status") in {"completed", "error"}:
            print(json.dumps(payload, indent=2))
            return 0 if payload.get("status") == "completed" else 1
        time.sleep(args.poll_interval_ms / 1000.0)
    print(json.dumps({"error": "request not completed before timeout", "request_id": args.request_id}, indent=2))
    return 1


def auth_login_command(args: argparse.Namespace) -> int:
    auth_path = Path(args.auth_path)
    save_auth_state({
        "gateway_url": args.gateway_url,
        "api_key": args.api_key,
    }, auth_path)
    print(json.dumps({
        "status": "ok",
        "auth_path": str(auth_path),
        "gateway_url": args.gateway_url,
    }, indent=2))
    return 0


def auth_status_command(args: argparse.Namespace) -> int:
    auth_path = Path(args.auth_path)
    state = load_auth_state(auth_path)
    print(json.dumps({
        "configured": bool(state.get("api_key")),
        "auth_path": str(auth_path),
        "gateway_url": state.get("gateway_url", ""),
        "api_key_present": bool(state.get("api_key")),
    }, indent=2))
    return 0


def auth_clear_command(args: argparse.Namespace) -> int:
    auth_path = Path(args.auth_path)
    if auth_path.exists():
        auth_path.unlink()
    print(json.dumps({
        "status": "cleared",
        "auth_path": str(auth_path),
    }, indent=2))
    return 0


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
