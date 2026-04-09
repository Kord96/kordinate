#!/usr/bin/env python3
"""Render focused summaries from Augur facts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def load_facts(path: Path) -> list[dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload.get("facts", [])


def render_view(facts: list[dict[str, Any]], name: str) -> str:
    if name == "api":
        selected = [f for f in facts if f.get("kind") == "route"]
    elif name == "data":
        selected = [f for f in facts if f.get("kind") in {"model", "state-store"}]
    elif name == "deps":
        selected = [f for f in facts if f.get("kind") in {"external-client", "import-edge"}]
    elif name == "auth":
        selected = [f for f in facts if f.get("kind") == "auth-surface"]
    elif name == "failures":
        selected = [f for f in facts if f.get("kind") == "external-client"]
    else:
        raise ValueError(f"unknown view: {name}")

    lines = [f"# {name}", ""]
    for fact in selected[:200]:
        lines.append(f"- {fact.get('summary','')} [{fact.get('id','')}]")
    if len(lines) == 2:
        lines.append("- No facts found.")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Render focused markdown views from Augur facts")
    parser.add_argument("facts", type=Path)
    parser.add_argument("view", choices=["api", "data", "deps", "auth", "failures"])
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    facts = load_facts(args.facts)
    rendered = render_view(facts, args.view)
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
