#!/usr/bin/env python3
"""Build a graph view of Augur concepts and frameworks."""

from __future__ import annotations

import json
import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
MEMORY = ROOT / "memory"
INDEXES = MEMORY / "indexes"

CONCEPT_DIR = MEMORY / "catalog" / "concepts"
FRAMEWORK_DIR = MEMORY / "catalog" / "frameworks"

FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)
CONCEPT_LINK_RE = re.compile(r"\(/concepts/([a-z0-9-]+)\)")


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def parse_frontmatter(text: str) -> tuple[dict, str]:
    match = FRONTMATTER_RE.match(text)
    if not match:
        return {}, text
    data = yaml.safe_load(match.group(1)) or {}
    body = text[match.end() :]
    return data, body


def title_from_body(body: str, fallback: str) -> str:
    for line in body.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return fallback


def concept_files() -> list[Path]:
    return [
        p
        for p in sorted(CONCEPT_DIR.glob("*.md"))
        if p.name not in {"README.md", "meta-schema.md"}
    ]


def framework_dirs() -> list[Path]:
    return [p for p in sorted(FRAMEWORK_DIR.iterdir()) if p.is_dir() and (p / "framework.md").exists()]


RELATION_MAP = {
    "is_a": "is_a",
    "part_of": "part_of",
    "related_to": "related_to",
    "preferred_over": "preferred_over",
    "disambiguates": "disambiguates",
    "implements": "implements",
    "supports": "supports",
    "uses": "uses",
}

RELATION_META = {
    "has_type": {"directed": True, "confidence": "derived"},
    "has_abstraction": {"directed": True, "confidence": "derived"},
    "references": {"directed": True, "confidence": "inferred"},
    "commonly_implies": {"directed": True, "confidence": "inferred"},
    "is_a": {"directed": True, "confidence": "authored"},
    "part_of": {"directed": True, "confidence": "authored"},
    "related_to": {"directed": False, "confidence": "authored"},
    "preferred_over": {"directed": True, "confidence": "authored"},
    "disambiguates": {"directed": True, "confidence": "authored"},
    "implements": {"directed": True, "confidence": "authored"},
    "supports": {"directed": True, "confidence": "authored"},
    "uses": {"directed": True, "confidence": "authored"},
    "uses_language": {"directed": True, "confidence": "derived"},
}


def build_maintenance(edges: list[dict]) -> dict:
    pair_has_authored: set[tuple[str, str]] = set()
    pair_has_inferred: set[tuple[str, str]] = set()

    for edge in edges:
        pair = (edge["source"], edge["target"])
        if edge.get("authored", False):
            pair_has_authored.add(pair)
        elif edge["relation"] in {"references", "commonly_implies"}:
            pair_has_inferred.add(pair)

    inferred_only = [
        {
            "source": edge["source"],
            "target": edge["target"],
            "relation": edge["relation"],
            "reason": "inferred-only edge without an authored relationship",
        }
        for edge in edges
        if not edge.get("authored", False)
        and edge["relation"] in {"references", "commonly_implies"}
        and (edge["source"], edge["target"]) not in pair_has_authored
    ]

    authored_edges = sum(1 for edge in edges if edge.get("authored", False))
    inferred_edges = sum(1 for edge in edges if not edge.get("authored", False))
    return {
        "authored_edge_count": authored_edges,
        "inferred_edge_count": inferred_edges,
        "low_confidence_reference_count": len(inferred_only),
        "low_confidence_references": sorted(
            inferred_only,
            key=lambda item: (item["relation"], item["source"], item["target"]),
        ),
    }


def concept_record(path: Path) -> tuple[dict, list[dict]]:
    text = read(path)
    frontmatter, body = parse_frontmatter(text)
    concept_id = path.stem
    title = title_from_body(body, concept_id)
    edges: list[dict] = []

    concept_node = {
        "id": f"concept:{concept_id}",
        "kind": "concept",
        "slug": concept_id,
        "label": title,
        "description": frontmatter.get("description", ""),
        "concept_type": frontmatter.get("type", "unknown"),
        "abstractions": list(frontmatter.get("abstraction", [])),
        "status": frontmatter.get("status", "unclassified"),
        "scope": frontmatter.get("scope"),
        "path": str(path.relative_to(ROOT)),
    }

    edges.append(
        {
            "source": f"concept:{concept_id}",
            "target": f"type:{concept_node['concept_type']}",
            "relation": "has_type",
            "authored": False,
        }
    )
    for abstraction in concept_node["abstractions"]:
        edges.append(
            {
                "source": f"concept:{concept_id}",
                "target": f"abstraction:{abstraction}",
                "relation": "has_abstraction",
                "authored": False,
            }
        )

    for rel_key, rel_name in RELATION_MAP.items():
        for target in frontmatter.get("relationships", {}).get(rel_key, []) or []:
            edges.append(
                {
                    "source": f"concept:{concept_id}",
                    "target": f"concept:{target}",
                    "relation": rel_name,
                    "authored": True,
                }
            )

    linked = sorted(set(CONCEPT_LINK_RE.findall(body)))
    for target in linked:
        if target != concept_id:
            edges.append(
                {
                    "source": f"concept:{concept_id}",
                    "target": f"concept:{target}",
                    "relation": "references",
                    "authored": False,
                }
            )

    return concept_node, edges


def framework_record(path: Path) -> tuple[dict, list[dict]]:
    framework_md = read(path / "framework.md")
    frontmatter, body = parse_frontmatter(framework_md)
    semantics_path = path / "semantics.yaml"
    semantics = yaml.safe_load(read(semantics_path)) if semantics_path.exists() else {}
    framework_id = path.name
    title = title_from_body(body, framework_id)

    node = {
        "id": f"framework:{framework_id}",
        "kind": "framework",
        "slug": framework_id,
        "label": title,
        "description": frontmatter.get("description", semantics.get("summary", "")),
        "language": semantics.get("language"),
        "traits": semantics.get("traits", {}),
        "path": str((path / "framework.md").relative_to(ROOT)),
    }
    edges: list[dict] = []
    if node["language"]:
        edges.append(
            {
                "source": f"framework:{framework_id}",
                "target": f"language:{node['language']}",
                "relation": "uses_language",
                "authored": False,
            }
        )
    node["status"] = semantics.get("status", "unclassified")
    node["scope"] = semantics.get("scope")
    for concept in semantics.get("common_concepts", []) or []:
        edges.append(
            {
                "source": f"framework:{framework_id}",
                "target": f"concept:{concept}",
                "relation": "commonly_implies",
                "authored": False,
            }
        )
    for rel_key, rel_name in RELATION_MAP.items():
        for target in semantics.get("relationships", {}).get(rel_key, []) or []:
            edges.append(
                {
                    "source": f"framework:{framework_id}",
                    "target": f"concept:{target}",
                    "relation": rel_name,
                    "authored": True,
                }
            )
    return node, edges


def mermaid_id(node_id: str) -> str:
    return node_id.replace(":", "_").replace("-", "_")


def build_graph() -> dict:
    nodes: list[dict] = []
    edges: list[dict] = []
    node_ids: set[str] = set()
    edge_keys: set[tuple[str, str, str, bool]] = set()
    authored_pairs: set[tuple[str, str]] = set()

    def add_node(node: dict) -> None:
        if node["id"] in node_ids:
            return
        node_ids.add(node["id"])
        nodes.append(node)

    def add_edge(edge: dict) -> None:
        source = edge["source"]
        target = edge["target"]
        relation = edge["relation"]
        authored = bool(edge.get("authored"))

        # Authoritative authored edges win over low-confidence inferred hints
        # between the same endpoints.
        if not authored and relation in {"references", "commonly_implies"} and (source, target) in authored_pairs:
            return

        key = (source, target, relation, authored)
        if key in edge_keys:
            return
        edge_keys.add(key)
        if authored:
            authored_pairs.add((source, target))
            before = len(edges)
            edges[:] = [
                existing
                for existing in edges
                if not (
                    not existing.get("authored", False)
                    and existing["relation"] in {"references", "commonly_implies"}
                    and existing["source"] == source
                    and existing["target"] == target
                )
            ]
            if len(edges) != before:
                edge_keys.clear()
                for existing in edges:
                    edge_keys.add(
                        (
                            existing["source"],
                            existing["target"],
                            existing["relation"],
                            bool(existing.get("authored")),
                        )
                    )
        edges.append(edge)

    for path in concept_files():
        node, rels = concept_record(path)
        add_node(node)
        for edge in rels:
            add_edge(edge)

    for path in framework_dirs():
        node, rels = framework_record(path)
        add_node(node)
        for edge in rels:
            add_edge(edge)

    for node in list(nodes):
        if node["kind"] == "concept":
            add_node(
                {
                    "id": f"type:{node['concept_type']}",
                    "kind": "concept_type",
                    "label": node["concept_type"],
                }
            )
            for abstraction in node["abstractions"]:
                add_node(
                    {
                        "id": f"abstraction:{abstraction}",
                        "kind": "abstraction",
                        "label": abstraction,
                    }
                )
        elif node["kind"] == "framework" and node.get("language"):
            add_node(
                {
                    "id": f"language:{node['language']}",
                    "kind": "language",
                    "label": node["language"],
                }
            )

    graph = {
        "relation_types": RELATION_META,
        "nodes": sorted(nodes, key=lambda n: (n["kind"], n["id"])),
        "edges": sorted(edges, key=lambda e: (e["relation"], e["source"], e["target"], not e.get("authored", False))),
    }
    graph["maintenance"] = build_maintenance(graph["edges"])
    return graph


def render_mermaid(graph: dict) -> str:
    maintenance = graph.get("maintenance", {})
    low_confidence = maintenance.get("low_confidence_references", [])
    lines = [
        "---",
        "description: Generated ontology graph index for Augur concepts and frameworks",
        "---",
        "# Ontology Graph",
        "",
        "Generated from `memory/catalog/concepts/*.md` and `memory/catalog/frameworks/*/semantics.yaml`.",
        "",
        "Authored relationship metadata comes from concept frontmatter and framework semantics.",
        "Framework-authored edges take precedence over inferred framework hints, and concept-authored edges take precedence over prose-link references.",
        "Plain prose links are kept as low-confidence inferred `references` edges for maintenance rather than treated as equal authority.",
        "",
        "## Maintenance",
        "",
        f"- Authored edges: `{maintenance.get('authored_edge_count', 0)}`",
        f"- Inferred edges: `{maintenance.get('inferred_edge_count', 0)}`",
        f"- Low-confidence inferred references needing review: `{maintenance.get('low_confidence_reference_count', 0)}`",
    ]

    if low_confidence:
        lines.extend(
            [
                "",
                "Top low-confidence inferred references:",
            ]
        )
        for edge in low_confidence[:12]:
            lines.append(
                f"- `{edge['source']}` `{edge['relation']}` `{edge['target']}`"
            )

    lines.extend(
        [
        "",
        "```mermaid",
        "graph TD",
        ]
    )

    seen = set()
    for node in graph["nodes"]:
        node_id = mermaid_id(node["id"])
        if node_id in seen:
            continue
        seen.add(node_id)
        label = node["label"].replace('"', "'")
        lines.append(f'  {node_id}["{label}"]')

    status_styles = {
        "primary": "fill:#d7f5d1,stroke:#2f6b2f,stroke-width:2px",
        "specialized": "fill:#e7f0ff,stroke:#315c99,stroke-width:1px",
        "supporting": "fill:#fff1cf,stroke:#9b6a00,stroke-width:1px",
        "compatibility": "fill:#f5e1f7,stroke:#7d3c8c,stroke-width:1px,stroke-dasharray: 4 2",
        "unclassified": "fill:#eeeeee,stroke:#777777,stroke-width:1px",
    }

    for idx, (status, style) in enumerate(status_styles.items()):
        lines.append(f"  classDef status_{idx} {style}")

    status_to_class = {status: f"status_{idx}" for idx, status in enumerate(status_styles)}
    for node in graph["nodes"]:
        if node["kind"] not in {"concept", "framework"}:
            continue
        lines.append(f"  class {mermaid_id(node['id'])} {status_to_class.get(node.get('status', 'unclassified'), status_to_class['unclassified'])}")

    edge_index = 0
    for edge in graph["edges"]:
        source = mermaid_id(edge["source"])
        target = mermaid_id(edge["target"])
        relation = edge["relation"].replace("_", " ")
        lines.append(f"  {source} -->|{relation}| {target}")
        if not edge.get("authored", False):
            lines.append(f"  linkStyle {edge_index} stroke-dasharray: 4 2")
        edge_index += 1

    lines.extend(["```", ""])
    return "\n".join(lines)


def main() -> int:
    INDEXES.mkdir(parents=True, exist_ok=True)
    graph = build_graph()
    (INDEXES / "ontology-graph.json").write_text(json.dumps(graph, indent=2, sort_keys=False) + "\n", encoding="utf-8")
    (INDEXES / "ontology-graph.md").write_text(render_mermaid(graph), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
