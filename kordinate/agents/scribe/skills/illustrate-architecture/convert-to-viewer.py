#!/usr/bin/env python3
"""Convert architecture.yaml to Cytoscape viewer JSON.

Usage:
    python3 convert-to-viewer.py <architecture.yaml> <output.json>

Reads the designer's architecture.yaml and produces architecture.json
for the ProjectExplorer viewer component. Handles:
  - Component hierarchy (children nesting → flat nodes with parent/hasChildren)
  - Structural edges (depends_on)
  - Flow edges (data_flows)
  - Render edges (orphan children get parent→child edge)
  - Dedup (drop dependency edges when flow edges exist for same pair)
  - State data (for Data tab)
  - Failure modes (for Resilience tab)
  - Data flow details (for Flows tab)
"""

import yaml
import json
import sys


TYPE_MAP = {
    "frontend": "component",
    "store": "library",
    "api": "service",
    "worker": "service",
    "cli": "service",
    "gateway": "external-service",
}


def walk_components(components, nodes, dep_edges, parent_id=None):
    """Recursively walk components, building nodes and dependency edges."""
    for comp in components:
        has_children = bool(comp.get("children"))
        node_type = "group" if has_children else TYPE_MAP.get(comp.get("type", ""), comp.get("type", "component"))

        node = {
            "id": comp["id"],
            "name": comp["name"],
            "description": comp.get("description", ""),
            "type": node_type,
            "hasChildren": has_children,
        }

        if parent_id:
            node["parent"] = parent_id

        modules = comp.get("modules", [])
        if modules:
            node["file"] = modules[0]

        if comp.get("exports"):
            node["exports"] = comp["exports"]

        nodes.append(node)

        # Dependency edges
        for dep in comp.get("depends_on", []):
            dep_edges.append({
                "source": comp["id"],
                "target": dep,
                "label": "uses",
                "flowId": "dependency",
            })

        if has_children:
            walk_components(comp["children"], nodes, dep_edges, comp["id"])


def extract_flow_edges(data_flows):
    """Convert data_flows steps into edges."""
    edges = []
    for flow in data_flows:
        for step in flow.get("steps", []):
            if step.get("to"):
                edges.append({
                    "source": step["component"],
                    "target": step["to"],
                    "label": flow.get("name", flow["id"]),
                    "flowId": flow["id"],
                })
    return edges


def add_render_edges(nodes, all_edges):
    """Add parent→child edges for orphan leaf nodes."""
    edge_nodes = set()
    for e in all_edges:
        edge_nodes.add(e["source"])
        edge_nodes.add(e["target"])

    render_edges = []
    for n in nodes:
        if n["id"] not in edge_nodes and not n.get("hasChildren") and n.get("parent"):
            render_edges.append({
                "source": n["parent"],
                "target": n["id"],
                "label": "renders",
                "flowId": "rendering",
            })

    return render_edges


def dedup_edges(flow_edges, dep_edges, render_edges):
    """Remove dependency/render edges that overlap with flow edges."""
    flow_pairs = set()
    for e in flow_edges:
        flow_pairs.add(tuple(sorted([e["source"], e["target"]])))

    filtered_dep = []
    for e in dep_edges:
        pair = tuple(sorted([e["source"], e["target"]]))
        if pair not in flow_pairs:
            filtered_dep.append(e)

    filtered_render = []
    all_pairs = flow_pairs | set(tuple(sorted([e["source"], e["target"]])) for e in filtered_dep)
    for e in render_edges:
        pair = tuple(sorted([e["source"], e["target"]]))
        if pair not in all_pairs:
            filtered_render.append(e)

    return flow_edges + filtered_dep + filtered_render


def extract_externals(arch, nodes):
    """Add external dependencies as nodes."""
    # Find or create External group
    ext_group_id = None
    for n in nodes:
        if n.get("type") == "group" and "external" in n["name"].lower():
            ext_group_id = n["id"]
            break

    if not ext_group_id:
        ext_group_id = "external-group"
        nodes.append({
            "id": ext_group_id,
            "name": "External",
            "description": "External APIs and services",
            "type": "group",
            "hasChildren": True,
        })

    for ext in arch.get("external_dependencies", []):
        # Don't add if already exists as a node
        if not any(n["id"] == ext["id"] for n in nodes):
            nodes.append({
                "id": ext["id"],
                "name": ext["name"],
                "description": ext.get("purpose", ""),
                "type": "external-service",
                "hasChildren": False,
                "parent": ext_group_id,
            })


def convert(arch):
    """Convert architecture dict to viewer JSON."""
    nodes = []
    dep_edges = []

    # Walk components
    walk_components(arch.get("components", []), nodes, dep_edges)

    # Add externals
    extract_externals(arch, nodes)

    # Flow edges
    flow_edges = extract_flow_edges(arch.get("data_flows", []))

    # Render edges for orphans
    render_edges = add_render_edges(nodes, flow_edges + dep_edges)

    # Dedup
    all_edges = dedup_edges(flow_edges, dep_edges, render_edges)

    # State data
    state = []
    for s in arch.get("state", []):
        state.append({
            "id": s["id"],
            "name": s.get("technology", s["id"]),
            "description": s.get("stores", ""),
            "purpose": s.get("purpose", ""),
            "technology": s.get("technology", ""),
            "component": s.get("component", ""),
            "persistence": s.get("persistence", ""),
        })

    # Failure modes
    failure_modes = []
    for f in arch.get("failure_modes", []):
        failure_modes.append({
            "id": f["id"],
            "trigger": f.get("trigger", ""),
            "severity": f.get("severity", ""),
            "impact": f.get("impact", ""),
            "cascade": f.get("cascade", []),
            "detection": f.get("detection", []),
            "recovery": f.get("recovery", []),
        })

    # Data flows (for Flows tab)
    data_flows = []
    for flow in arch.get("data_flows", []):
        data_flows.append({
            "id": flow["id"],
            "name": flow.get("name", ""),
            "description": flow.get("description", ""),
            "trigger": flow.get("trigger", ""),
            "steps": flow.get("steps", []),
        })

    return {
        "nodes": nodes,
        "edges": all_edges,
        "state": state,
        "failure_modes": failure_modes,
        "data_flows": data_flows,
    }


def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <architecture.yaml> <output.json>")
        sys.exit(1)

    yaml_path = sys.argv[1]
    json_path = sys.argv[2]

    with open(yaml_path) as f:
        arch = yaml.safe_load(f)

    result = convert(arch)

    with open(json_path, "w") as f:
        json.dump(result, f, indent=2)

    # Report
    nodes = result["nodes"]
    edges = result["edges"]
    roots = [n for n in nodes if not n.get("parent")]
    groups = [n for n in nodes if n.get("hasChildren")]
    edge_nodes = set()
    for e in edges:
        edge_nodes.add(e["source"])
        edge_nodes.add(e["target"])
    orphans = [n for n in nodes if n["id"] not in edge_nodes and not n.get("hasChildren")]

    print(f"Nodes: {len(nodes)} ({len(roots)} roots, {len(groups)} groups)")
    print(f"Edges: {len(edges)}")
    print(f"Orphans: {len(orphans)}")
    print(f"State: {len(result['state'])}")
    print(f"Failure modes: {len(result['failure_modes'])}")
    print(f"Data flows: {len(result['data_flows'])}")
    print(f"Written to {json_path}")


if __name__ == "__main__":
    main()
