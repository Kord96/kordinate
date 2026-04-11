#!/usr/bin/env python3
from __future__ import annotations

import argparse
import base64
import json
import shlex
import subprocess
import urllib.error
import urllib.request
from pathlib import Path

import yaml


def load_agent_spec(path: Path) -> list[dict]:
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    agents = data.get("agents")
    if not isinstance(agents, list):
        raise SystemExit(f"invalid agent spec: {path}")
    return agents


def kubectl_json(kubectl_cmd: list[str], args: list[str]) -> dict:
    completed = subprocess.run(
        [*kubectl_cmd, *args, "-o", "json"],
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        raise RuntimeError(completed.stderr.strip() or completed.stdout.strip() or "kubectl failed")
    return json.loads(completed.stdout)


def load_secret_value(kubectl_cmd: list[str], namespace: str, secret_name: str, secret_key: str) -> str:
    payload = kubectl_json(kubectl_cmd, ["-n", namespace, "get", "secret", secret_name])
    encoded = ((payload.get("data") or {}) if isinstance(payload, dict) else {}).get(secret_key)
    if not encoded:
        raise RuntimeError(f"missing key {secret_key} in secret/{secret_name}")
    return base64.b64decode(encoded).decode("utf-8")


def validate_key_shape(provider: str, key_value: str) -> str | None:
    stripped = key_value.strip()
    if not stripped:
        return "secret value is empty"
    if provider == "anthropic" and not stripped.startswith("sk-ant-"):
        return "Anthropic key does not start with sk-ant-"
    if provider in {"openai", "codex"} and not stripped.startswith("sk-"):
        return "OpenAI key does not start with sk-"
    return None


def openai_chat_probe(base_url: str, key_value: str, model: str) -> tuple[bool, str]:
    url = f"{base_url.rstrip('/')}/chat/completions"
    request = urllib.request.Request(
        url,
        data=json.dumps({
            "model": model,
            "messages": [{"role": "user", "content": "ping"}],
            "max_tokens": 1,
        }).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {key_value}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    return perform_probe(request)


def openai_responses_probe(base_url: str, key_value: str, model: str) -> tuple[bool, str]:
    url = f"{base_url.rstrip('/')}/responses"
    request = urllib.request.Request(
        url,
        data=json.dumps({
            "model": model,
            "input": "ping",
            "max_output_tokens": 16,
        }).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {key_value}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    return perform_probe(request)


def anthropic_probe(key_value: str) -> tuple[bool, str]:
    request = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=json.dumps({
            "model": "claude-sonnet-4-5",
            "max_tokens": 1,
            "messages": [{"role": "user", "content": "ping"}],
        }).encode("utf-8"),
        headers={
            "x-api-key": key_value,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    return perform_probe(request)


def perform_probe(request: urllib.request.Request) -> tuple[bool, str]:
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            body = response.read().decode("utf-8", errors="replace")
            return True, f"ok ({response.status}) {body[:200]}"
    except urllib.error.HTTPError as error:
        body = error.read().decode("utf-8", errors="replace")
        return False, f"http {error.code}: {body[:300]}"
    except Exception as error:  # pragma: no cover - network/runtime failures
        return False, str(error)


def probe_provider(provider: str, base_url: str | None, key_value: str, model: str) -> tuple[bool, str]:
    normalized = provider.strip().lower()
    if normalized == "anthropic":
        return anthropic_probe(key_value)
    if normalized in {"openai", "codex"}:
        if not base_url:
            return False, "missing base_url for OpenAI probe"
        return openai_responses_probe(base_url, key_value, model)
    if normalized in {"deepseek", "fireworks", "gemini"}:
        if not base_url:
            return False, "missing base_url for OpenAI-compatible probe"
        return openai_chat_probe(base_url, key_value, model)
    return True, "probe skipped for provider"


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate provider secrets referenced by the agent platform spec.")
    parser.add_argument(
        "--spec",
        default="agents/charon/skills/platform/agent-spec.yaml",
        help="path to agent-spec.yaml",
    )
    parser.add_argument("--namespace", default="kord", help="Kubernetes namespace for agent secrets")
    parser.add_argument(
        "--kubectl",
        default="kubectl",
        help='kubectl command to use, for example: --kubectl "sudo k3s kubectl"',
    )
    parser.add_argument("--agent", action="append", dest="agents", help="specific agent name to validate")
    parser.add_argument(
        "--probe-provider",
        action="store_true",
        help="call the provider API with the referenced key instead of only validating presence/shape",
    )
    args = parser.parse_args()

    spec_path = Path(args.spec)
    agents = load_agent_spec(spec_path)
    selected = set(args.agents or [])
    kubectl_cmd = shlex.split(args.kubectl)

    failures = 0
    for agent in agents:
        name = agent.get("name") or "<unknown>"
        if selected and name not in selected:
            continue
        daemon = (((agent.get("runtime") or {}).get("daemon") or {}) if isinstance(agent.get("runtime"), dict) else {})
        secret = daemon.get("secret") or {}
        if not isinstance(secret, dict) or not secret.get("name") or not secret.get("key"):
            continue

        provider = str(daemon.get("provider") or "unknown")
        model = str(daemon.get("model") or "")
        base_url = None
        backend = daemon.get("backend")
        if isinstance(backend, dict):
            base_url = backend.get("base_url")

        try:
            key_value = load_secret_value(kubectl_cmd, args.namespace, str(secret["name"]), str(secret["key"]))
            shape_error = validate_key_shape(provider, key_value)
            if shape_error:
                print(f"[FAIL] {name}: {shape_error}")
                failures += 1
                continue

            if args.probe_provider:
                ok, message = probe_provider(provider, base_url, key_value, model)
                status = "OK" if ok else "FAIL"
                print(f"[{status}] {name}: {provider}/{model} via secret/{secret['name']} -> {message}")
                if not ok:
                    failures += 1
            else:
                print(f"[OK] {name}: secret/{secret['name']} present and shape-valid for {provider}/{model}")
        except Exception as error:
            print(f"[FAIL] {name}: {error}")
            failures += 1

    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
