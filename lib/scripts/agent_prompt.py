#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import selectors
import shlex
import subprocess
import sys
import time
import urllib.request
from typing import Any


DEFAULT_DISCOVERY_URL = os.environ.get("KORD_API_URL", "http://kord-api.kord.svc.cluster.local:9091")
DEFAULT_KAFKA_NAMESPACE = "dev"
DEFAULT_KAFKA_POD = "kafka-combined-0"
DEFAULT_DISCOVERY_NAMESPACE = "kord"
DEFAULT_DISCOVERY_TARGET = "deploy/kord-api"
DEFAULT_KAFKA_BOOTSTRAP = "kafka-kafka-bootstrap.dev.svc.cluster.local:9092"
DEFAULT_GATEWAY_URL = os.environ.get("KORD_API_URL", os.environ.get("KORD_GATEWAY_URL", ""))
DEFAULT_API_KEY = os.environ.get("KORD_API_KEY", "")
KAFKA_BIN = "/opt/kafka/bin"
KUBECTL_CMD = shlex.split(os.environ.get("KUBECTL_CMD", "kubectl"))


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


def fetch_discovery_via_kubectl(namespace: str, target: str, path: str) -> Any:
    script = (
        "python3 -c "
        + shlex.quote(
            "import json, urllib.request; "
            f"print(json.dumps(json.load(urllib.request.urlopen('http://127.0.0.1:9091{path}'))))"
        )
    )
    raw = kubectl_exec(namespace, target, script).strip()
    return json.loads(raw)


def discovery_payload(args: argparse.Namespace) -> Any:
    path = f"/agents/{args.agent}" if getattr(args, "agent", None) else "/agents"
    if getattr(args, "verbose", False):
        sep = "&" if "?" in path else "?"
        path = f"{path}{sep}verbose=1"
    if getattr(args, "gateway_url", ""):
        headers = {}
        if getattr(args, "api_key", ""):
            headers["x-api-key"] = args.api_key
        return fetch_json_with_headers(f"{args.gateway_url.rstrip('/')}{path}", headers)
    if args.discovery_url:
        try:
            return fetch_json(f"{args.discovery_url.rstrip('/')}{path}")
        except Exception:
            pass
    return fetch_discovery_via_kubectl(args.discovery_namespace, args.discovery_target, path)


def kubectl_exec(namespace: str, pod: str, command: str, stdin_text: str | None = None) -> str:
    proc = subprocess.run(
        [
            *KUBECTL_CMD,
            "-n",
            namespace,
            "exec",
            "-i" if stdin_text is not None else "-t",
            pod,
            "--",
            "sh",
            "-lc",
            command,
        ] if stdin_text is not None else [
            *KUBECTL_CMD,
            "-n",
            namespace,
            "exec",
            pod,
            "--",
            "sh",
            "-lc",
            command,
        ],
        input=stdin_text,
        text=True,
        capture_output=True,
        check=True,
    )
    return proc.stdout


def kubectl_exec_retry(namespace: str, pod: str, command: str, stdin_text: str | None = None, attempts: int = 4) -> str:
    last_error: subprocess.CalledProcessError | None = None
    for attempt in range(1, attempts + 1):
        try:
            return kubectl_exec(namespace, pod, command, stdin_text=stdin_text)
        except subprocess.CalledProcessError as error:
            last_error = error
            if attempt == attempts:
                stderr = (error.stderr or "").strip()
                stdout = (error.stdout or "").strip()
                details = "\n".join(part for part in [stderr, stdout] if part)
                raise RuntimeError(details or str(error)) from error
            time.sleep(min(2 * attempt, 5))
    raise RuntimeError(str(last_error))


def consume_until_match(
    namespace: str,
    pod: str,
    bootstrap_server: str,
    topic: str,
    correlation_id: str,
    wait_ms: int,
) -> tuple[dict[str, Any] | None, int]:
    proc = subprocess.Popen(
        [
            *KUBECTL_CMD,
            "-n",
            namespace,
            "exec",
            pod,
            "--",
            "sh",
            "-lc",
            f"{KAFKA_BIN}/kafka-console-consumer.sh "
            f"--bootstrap-server {bootstrap_server} "
            f"--topic {topic} --from-beginning --timeout-ms {wait_ms} 2>/dev/null",
        ],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    selector = selectors.DefaultSelector()
    assert proc.stdout is not None
    selector.register(proc.stdout, selectors.EVENT_READ)

    deadline = time.time() + (wait_ms / 1000.0) + 2
    raw_lines = 0
    matched: dict[str, Any] | None = None

    try:
        while time.time() < deadline:
            events = selector.select(timeout=1.0)
            if not events:
                if proc.poll() is not None:
                    break
                continue
            for key, _ in events:
                line = key.fileobj.readline()
                if not line:
                    continue
                raw_lines += 1
                try:
                    candidate = json.loads(line)
                except Exception:
                    continue
                if isinstance(candidate, dict) and candidate.get("correlation_id") == correlation_id:
                    matched = candidate
                    return matched, raw_lines
            if proc.poll() is not None:
                break
        return matched, raw_lines
    finally:
        try:
            proc.terminate()
            proc.wait(timeout=2)
        except Exception:
            proc.kill()
            try:
                proc.wait(timeout=1)
            except Exception:
                pass


def discover(args: argparse.Namespace) -> int:
    payload = discovery_payload(args)
    print(json.dumps(payload, indent=2))
    return 0


def prompt(args: argparse.Namespace) -> int:
    if getattr(args, "gateway_url", ""):
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
        start = time.time()
        headers = {}
        if getattr(args, "api_key", ""):
            headers["x-api-key"] = args.api_key
        response = post_json(f"{args.gateway_url.rstrip('/')}/agents/{args.agent}/prompt", payload, headers)
        wall_ms = int((time.time() - start) * 1000)
        if isinstance(response, dict):
            response.setdefault("metadata", {})
            response["metadata"].setdefault("caller_timing", {})
            response["metadata"]["caller_timing"]["wall_ms"] = wall_ms
        print(json.dumps(response, indent=2))
        return 0

    request_topic = args.agent
    if args.discovery_url:
        try:
            payload = discovery_payload(args)
            request_topic = payload.get("request_topic", args.agent)
        except Exception:
            pass

    correlation_id = args.correlation_id or f"{args.agent}-{int(time.time())}"
    reply_topic = args.reply_topic or (
        f"{args.agent}-reply-{args.session_id}" if args.session_id else f"{args.agent}-reply-{int(time.time())}"
    )
    request = {
        "type": "request",
        "sender": reply_topic,
        "correlation_id": correlation_id,
        "prompt": args.prompt,
    }
    if args.working_dir:
        request["working_dir"] = args.working_dir
    if args.timeout_ms is not None:
        request["timeout_ms"] = args.timeout_ms
    if args.reflect:
        request["reflect"] = True
    if args.reflection_prompt:
        request["reflection_prompt"] = args.reflection_prompt
    if args.session_id:
        request["session_id"] = args.session_id

    start = time.time()
    kubectl_exec_retry(
        args.kafka_namespace,
        args.kafka_pod,
        f"{KAFKA_BIN}/kafka-topics.sh --bootstrap-server {args.kafka_bootstrap_server} --create --if-not-exists --topic {reply_topic} --partitions 1 --replication-factor 1 >/dev/null",
    )
    message_line = f"{reply_topic}\t{json.dumps(request)}\n"
    kubectl_exec_retry(
        args.kafka_namespace,
        args.kafka_pod,
        f"{KAFKA_BIN}/kafka-console-producer.sh --bootstrap-server {args.kafka_bootstrap_server} "
        f"--topic {request_topic} --property parse.key=true --property key.separator=$'\\t' >/dev/null 2>&1",
        stdin_text=message_line,
    )
    wall_ms = int((time.time() - start) * 1000)
    payload, raw_lines = consume_until_match(
        args.kafka_namespace,
        args.kafka_pod,
        args.kafka_bootstrap_server,
        reply_topic,
        correlation_id,
        args.wait_ms,
    )

    wall_ms = int((time.time() - start) * 1000)
    if payload is None and raw_lines == 0:
        print(json.dumps({"error": "no reply received", "wall_ms": wall_ms}, indent=2))
        return 1

    if payload is None:
        print(json.dumps({
            "error": "no matching reply received",
            "correlation_id": correlation_id,
            "reply_topic": reply_topic,
            "wall_ms": wall_ms,
            "raw_lines": raw_lines,
        }, indent=2))
        return 1

    payload.setdefault("metadata", {})
    payload["metadata"].setdefault("caller_timing", {})
    payload["metadata"]["caller_timing"]["wall_ms"] = wall_ms
    print(json.dumps(payload, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Discover and prompt daemon-backed agent pods")
    sub = parser.add_subparsers(dest="command", required=True)

    discover_parser = sub.add_parser("discover", help="return the discovery response")
    discover_parser.add_argument("--discovery-url", default=DEFAULT_DISCOVERY_URL)
    discover_parser.add_argument("--gateway-url", default=DEFAULT_GATEWAY_URL)
    discover_parser.add_argument("--api-key", default=DEFAULT_API_KEY)
    discover_parser.add_argument("--agent")
    discover_parser.add_argument("--verbose", action="store_true")
    discover_parser.add_argument("--discovery-namespace", default=DEFAULT_DISCOVERY_NAMESPACE)
    discover_parser.add_argument("--discovery-target", default=DEFAULT_DISCOVERY_TARGET)
    discover_parser.set_defaults(func=discover)

    prompt_parser = sub.add_parser("prompt", help="send one request to an agent and wait for a reply")
    prompt_parser.add_argument("agent")
    prompt_parser.add_argument("prompt")
    prompt_parser.add_argument("--working-dir")
    prompt_parser.add_argument("--timeout-ms", type=int)
    prompt_parser.add_argument("--reflect", action="store_true")
    prompt_parser.add_argument("--reflection-prompt")
    prompt_parser.add_argument("--reply-topic")
    prompt_parser.add_argument("--session-id", help="Stable session lane; reuses the same reply topic for sticky routing")
    prompt_parser.add_argument("--correlation-id")
    prompt_parser.add_argument("--wait-ms", type=int, default=120000)
    prompt_parser.add_argument("--async", dest="async_mode", action="store_true")
    prompt_parser.add_argument("--discovery-url", default=DEFAULT_DISCOVERY_URL)
    prompt_parser.add_argument("--gateway-url", default=DEFAULT_GATEWAY_URL)
    prompt_parser.add_argument("--api-key", default=DEFAULT_API_KEY)
    prompt_parser.add_argument("--discovery-namespace", default=DEFAULT_DISCOVERY_NAMESPACE)
    prompt_parser.add_argument("--discovery-target", default=DEFAULT_DISCOVERY_TARGET)
    prompt_parser.add_argument("--kafka-namespace", default=DEFAULT_KAFKA_NAMESPACE)
    prompt_parser.add_argument("--kafka-pod", default=DEFAULT_KAFKA_POD)
    prompt_parser.add_argument("--kafka-bootstrap-server", default=DEFAULT_KAFKA_BOOTSTRAP)
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


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
