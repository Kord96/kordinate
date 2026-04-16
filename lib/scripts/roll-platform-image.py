#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
from pathlib import Path

import yaml


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Roll platform deployments affected by a given image.")
    parser.add_argument("image", help="image name such as agent-augur or agent-base")
    parser.add_argument("registry", help="resolved registry host, e.g. localhost:30500")
    parser.add_argument("tag", help="image tag to roll")
    parser.add_argument("--env", default="dev", help="target namespace/environment")
    parser.add_argument(
        "--spec",
        default="agents/charon/skills/platform/agent-spec.yaml",
        help="path to the Charon platform spec",
    )
    parser.add_argument("--dry-run", action="store_true", help="print affected deployments without changing them")
    return parser.parse_args()


def load_spec(spec_path: Path) -> dict:
    return yaml.safe_load(spec_path.read_text(encoding="utf-8"))


def image_for_agent(agent: dict) -> str:
    customization = (agent.get("image") or {}).get("customization")
    if not customization or customization == "none":
        return "agent-base"
    return str(customization)


def affected_agents(spec: dict, image: str) -> list[str]:
    return [agent["name"] for agent in spec.get("agents", []) if image_for_agent(agent) == image]


def run(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True)


def main() -> int:
    args = parse_args()
    spec_path = Path(args.spec).resolve()
    spec = load_spec(spec_path)
    targets = affected_agents(spec, args.image)
    if not targets:
      raise SystemExit(f"no agents in {spec_path} use image {args.image!r}")

    image_ref = f"{args.registry}/{args.image}:{args.tag}"
    for agent_name in targets:
        deployment = f"deployment/agent-{agent_name}"
        set_image_cmd = [
            "kubectl",
            "-n",
            args.env,
            "set",
            "image",
            deployment,
            f"setup={image_ref}",
            f"agent={image_ref}",
        ]
        if args.dry_run:
            print(" ".join(set_image_cmd))
            continue
        run(set_image_cmd)
        run(["kubectl", "-n", args.env, "rollout", "status", deployment, "--timeout=300s"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
