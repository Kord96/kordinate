#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

import yaml


SPECIAL_FLAVORS = {"augur", "charon", "alfred", "sauron", "warden"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Append a daemon-backed agent entry to Charon platform agent-spec.yaml")
    parser.add_argument("name", help="Deployed agent name")
    parser.add_argument("--spec", default="agents/charon/skills/platform/agent-spec.yaml", help="Path to agent-spec.yaml")
    parser.add_argument("--profiles", default="agents/charon/skills/platform/agent-creation-profiles.yaml", help="Path to agent creation profiles")
    parser.add_argument("--profile", default="generic", help="Creation profile name")
    parser.add_argument("--flavor", default="", help="Agent flavor to seed")
    parser.add_argument("--provider", default="", help="Daemon provider")
    parser.add_argument("--model", default="", help="Daemon model")
    parser.add_argument("--backend", default="", help="Backend name override (defaults to provider)")
    parser.add_argument("--image-customization", default="", help="Image customization name or 'none'")
    parser.add_argument("--runtime-kind", default="", help="runtime.daemon.kind value")
    parser.add_argument("--secret-env", default="", help="Environment variable name used by the runtime for the provider API key")
    parser.add_argument("--secret-name", default="", help="Kubernetes Secret name to mount into the agent pod")
    parser.add_argument("--secret-key", default="", help="Kubernetes Secret data key to mount into the agent pod")
    parser.add_argument("--memory-bundle", default="", help="Specialist memory bundle name when required by the creation profile")
    parser.add_argument("--runtime-bundle", default="", help="Specialist runtime bundle name when required by the creation profile")
    parser.add_argument("--working-directory", default="", help="Optional daemon working directory")
    parser.add_argument("--skip-git-repo-check", action="store_true", help="Set CODEX_SKIP_GIT_REPO_CHECK=true")
    parser.add_argument("--min-replicas", type=int, default=0)
    parser.add_argument("--max-replicas", type=int, default=3)
    parser.add_argument("--cooldown", type=int, default=300)
    parser.add_argument("--request-cpu", default="100m")
    parser.add_argument("--request-memory", default="512Mi")
    parser.add_argument("--limit-memory", default="4Gi")
    return parser.parse_args()


def load_profiles(path: str) -> dict:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return payload.get("profiles", {})


def resolve_profile(args: argparse.Namespace, profiles: dict) -> dict:
    if args.profile not in profiles:
        raise SystemExit(f"unknown creation profile '{args.profile}'")
    profile = profiles[args.profile]
    defaults = profile.get("defaults", {})
    resolved = {
        "profile": args.profile,
        "flavor": args.flavor or defaults.get("flavor", "generic"),
        "provider": args.provider or defaults.get("provider", "anthropic"),
        "model": args.model or defaults.get("model", "sonnet"),
        "backend": args.backend or defaults.get("backend") or args.provider or defaults.get("provider", "anthropic"),
        "image_customization": args.image_customization or defaults.get("image_customization", "none"),
        "runtime_kind": args.runtime_kind or defaults.get("runtime_kind", "openclaude-harness"),
        "secret_env": args.secret_env or defaults.get("secret_env", ""),
        "secret_name": args.secret_name or defaults.get("secret_name", ""),
        "secret_key": args.secret_key or defaults.get("secret_key", "api-key"),
        "memory_bundle": args.memory_bundle,
        "runtime_bundle": args.runtime_bundle,
        "required_choices": profile.get("required_choices", []),
        "choices": profile.get("choices", {}),
    }
    for field in resolved["required_choices"]:
        if not resolved.get(field):
            raise SystemExit(f"profile '{args.profile}' requires --{field.replace('_', '-')}")
        allowed = resolved["choices"].get(field, {}).get("allowed", [])
        if allowed and resolved[field] not in allowed:
            raise SystemExit(f"invalid {field} '{resolved[field]}' for profile '{args.profile}'. Allowed: {', '.join(allowed)}")
    return resolved


def build_agent(args: argparse.Namespace) -> dict:
    name = args.name
    profiles = load_profiles(args.profiles)
    profile = resolve_profile(args, profiles)
    flavor = profile["flavor"]
    backend = profile["backend"]
    agent = {
        "name": name,
        "flavor": flavor,
        "image": {
            "base": "agent-base",
            "customization": profile["image_customization"],
        },
        "runtime": {
            "command": ["klaude-daemon"],
            "daemon": {
                "kind": profile["runtime_kind"],
                "provider": profile["provider"],
                "model": profile["model"],
                "backend": {"name": backend},
            },
            "kafka": {
                "request_topic": f"agent.{name}",
                "reply_required": True,
                "request_schema": {
                    "required": ["prompt", "reply_to"],
                    "optional": ["timeout_ms", "reflect"],
                },
                "response_schema": {
                    "required": ["status", "output"],
                    "optional": ["reflection", "errors"],
                },
            },
            "state": {
                "project_dir": f"/runtime/{name}",
                "state_dir": f"/kord/{name}",
            },
        },
        "creation": {
            "profile": profile["profile"],
        },
        "deploy": {
            "replicas": {
                "min": args.min_replicas,
                "max": args.max_replicas,
                "cooldown": args.cooldown,
            },
            "resources": {
                "requests": {
                    "cpu": args.request_cpu,
                    "memory": args.request_memory,
                },
                "limits": {
                    "memory": args.limit_memory,
                },
            },
        },
    }
    if profile["memory_bundle"]:
        agent["creation"]["memory_bundle"] = profile["memory_bundle"]
    if profile["runtime_bundle"]:
        agent["creation"]["runtime_bundle"] = profile["runtime_bundle"]
    if profile["secret_env"] and profile["secret_name"]:
        agent["runtime"]["daemon"]["secret"] = {
            "env": profile["secret_env"],
            "name": profile["secret_name"],
            "key": profile["secret_key"] or "api-key",
        }
    if args.working_directory:
        agent["runtime"]["daemon"]["working_directory"] = args.working_directory
    if args.skip_git_repo_check:
        agent["runtime"]["daemon"]["skip_git_repo_check"] = True
    if flavor in SPECIAL_FLAVORS and flavor != name and profile["image_customization"] == "none":
        agent["image"]["customization"] = f"agent-{flavor}"
    return agent


def main() -> int:
    args = parse_args()
    spec_path = Path(args.spec)
    payload = yaml.safe_load(spec_path.read_text(encoding="utf-8"))
    agents = payload.setdefault("agents", [])
    if any(agent.get("name") == args.name for agent in agents):
        raise SystemExit(f"agent '{args.name}' already exists in {spec_path}")
    agents.append(build_agent(args))
    spec_path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
