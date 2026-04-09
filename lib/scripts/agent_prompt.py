#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
import urllib.request
from typing import Any


DEFAULT_DISCOVERY_URL = "http://klaude-discovery.kord.svc.cluster.local:9091"
DEFAULT_KAFKA_NAMESPACE = "dev"
DEFAULT_KAFKA_POD = "kafka-combined-0"
KAFKA_BIN = "/opt/kafka/bin"


def fetch_json(url: str) -> Any:
    with urllib.request.urlopen(url) as response:
        return json.loads(response.read().decode("utf-8"))


def kubectl_exec(namespace: str, pod: str, command: str, stdin_text: str | None = None) -> str:
    proc = subprocess.run(
        [
            "kubectl",
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
            "kubectl",
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


def discover(args: argparse.Namespace) -> int:
    url = args.discovery_url.rstrip("/")
    payload = fetch_json(f"{url}/agents/{args.agent}" if args.agent else f"{url}/agents")
    print(json.dumps(payload, indent=2))
    return 0


def prompt(args: argparse.Namespace) -> int:
    request_topic = args.agent
    if args.discovery_url:
        try:
            payload = fetch_json(f"{args.discovery_url.rstrip('/')}/agents/{args.agent}")
            request_topic = payload.get("request_topic", args.agent)
        except Exception:
            pass

    correlation_id = args.correlation_id or f"{args.agent}-{int(time.time())}"
    reply_topic = args.reply_topic or f"{args.agent}-reply-{int(time.time())}"
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

    start = time.time()
    kubectl_exec(
        args.kafka_namespace,
        args.kafka_pod,
        f"{KAFKA_BIN}/kafka-topics.sh --bootstrap-server localhost:9092 --create --if-not-exists --topic {reply_topic} --partitions 1 --replication-factor 1 >/dev/null",
    )
    kubectl_exec(
        args.kafka_namespace,
        args.kafka_pod,
        f"{KAFKA_BIN}/kafka-console-producer.sh --bootstrap-server localhost:9092 --topic {request_topic} >/dev/null 2>&1",
        stdin_text=json.dumps(request) + "\n",
    )
    raw = kubectl_exec(
        args.kafka_namespace,
        args.kafka_pod,
        f"{KAFKA_BIN}/kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic {reply_topic} --from-beginning --timeout-ms {args.wait_ms} 2>/dev/null",
    ).strip()

    wall_ms = int((time.time() - start) * 1000)
    if not raw:
        print(json.dumps({"error": "no reply received", "wall_ms": wall_ms}, indent=2))
        return 1

    try:
        payload = json.loads(raw.splitlines()[-1])
    except Exception:
        print(raw)
        return 0

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
    discover_parser.add_argument("--agent")
    discover_parser.set_defaults(func=discover)

    prompt_parser = sub.add_parser("prompt", help="send one request to an agent and wait for a reply")
    prompt_parser.add_argument("agent")
    prompt_parser.add_argument("prompt")
    prompt_parser.add_argument("--working-dir")
    prompt_parser.add_argument("--timeout-ms", type=int)
    prompt_parser.add_argument("--reflect", action="store_true")
    prompt_parser.add_argument("--reflection-prompt")
    prompt_parser.add_argument("--reply-topic")
    prompt_parser.add_argument("--correlation-id")
    prompt_parser.add_argument("--wait-ms", type=int, default=120000)
    prompt_parser.add_argument("--discovery-url", default=DEFAULT_DISCOVERY_URL)
    prompt_parser.add_argument("--kafka-namespace", default=DEFAULT_KAFKA_NAMESPACE)
    prompt_parser.add_argument("--kafka-pod", default=DEFAULT_KAFKA_POD)
    prompt_parser.set_defaults(func=prompt)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
