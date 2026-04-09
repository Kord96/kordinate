#!/usr/bin/env python3
"""Compute blast radius from Augur facts."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict, deque
from pathlib import Path
from typing import Any


def load_payload(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_facts(path: Path) -> list[dict[str, Any]]:
    payload = load_payload(path)
    if path.is_dir():
        facts: list[dict[str, Any]] = []
        index = path / "index.json"
        if index.exists():
            payload = load_payload(index)
            for domain in payload.get("index", {}).get("domains", []):
                file = path.parent / domain.get("file", "")
                if file.exists():
                    data = load_payload(file)
                    facts.extend(data.get("facts", []))
            return facts
        for file in path.glob("*.json"):
            data = load_payload(file)
            facts.extend(data.get("facts", []))
        return facts
    return payload.get("facts", [])


def source_path(value: str) -> str:
    return value.split(":", 1)[0]


def build_graph(facts: list[dict[str, Any]]) -> tuple[dict[str, set[str]], dict[str, list[dict[str, Any]]]]:
    graph: dict[str, set[str]] = defaultdict(set)
    by_file: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for fact in facts:
        for source in fact.get("source_files", []):
            by_file[source_path(source)].append(fact)
        if fact.get("kind") != "import-edge":
            continue
        raw = fact.get("raw_evidence", {})
        src = raw.get("from")
        dst = raw.get("to")
        if src and dst:
            graph[str(src)].add(str(dst))
    return graph, by_file


def compute_blast(graph: dict[str, set[str]], start: str, max_depth: int) -> dict[str, int]:
    visited = {start: 0}
    queue = deque([(start, 0)])
    while queue:
        node, depth = queue.popleft()
        if depth >= max_depth:
            continue
        for neighbor in graph.get(node, set()):
            if neighbor in visited:
                continue
            visited[neighbor] = depth + 1
            queue.append((neighbor, depth + 1))
    return visited


def main() -> int:
    parser = argparse.ArgumentParser(description="Compute blast radius from Augur facts")
    parser.add_argument("facts", type=Path, help="Path to facts JSON or facts directory")
    parser.add_argument("target", help="File/module to analyze")
    parser.add_argument("--max-depth", type=int, default=3)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    facts = load_facts(args.facts)
    graph, by_file = build_graph(facts)
    blast = compute_blast(graph, args.target, args.max_depth)
    related_facts = {node: len(by_file.get(node, [])) for node in blast}
    result = {
        "target": args.target,
        "max_depth": args.max_depth,
        "affected_modules": [{"id": node, "depth": depth, "fact_count": related_facts.get(node, 0)} for node, depth in sorted(blast.items(), key=lambda item: (item[1], item[0]))],
    }
    rendered = json.dumps(result, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
