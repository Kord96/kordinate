#!/usr/bin/env python3
"""Convert atlas.json to Cytoscape viewer JSON.

Usage:
    python3 convert-to-viewer.py <atlas.json> <output.json>

This is the reference implementation for the illustrate-architecture skill.
The scribe LLM should use its judgment to produce the JSON, using this
script as a fallback for validation.

Rules encoded here:
  1. Components with children → group nodes (hasChildren=true)
  2. depends_on → structural "uses" edges
  3. flows → flow edges between consecutive steps (typed: data, control, event, state, resource)
  4. No render edges — containment communicates parent-child visually
  5. Dedup: drop dependency edges when a flow edge exists for the same pair
  6. Bidirectional flows: keep both arrows, hide label on the return edge
  7. State, failure_modes, flows included for Data/Resilience/Flows tabs
  8. External dependencies added as nodes under an "External" group
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
        node_type = "group" if has_children else TYPE_MAP.get(
            comp.get("type", ""), comp.get("type", "component")
        )

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

        for dep in comp.get("depends_on", []):
            dep_edges.append({
                "source": comp["id"],
                "target": dep,
                "label": "uses",
                "flowId": "dependency",
            })

        if has_children:
            walk_components(comp["children"], nodes, dep_edges, comp["id"])


def extract_flow_edges(flows):
    """Convert typed flows steps into edges."""
    edges = []
    for flow in flows:
        flow_type = flow.get("type", "data")
        for step in flow.get("steps", []):
            if step.get("to"):
                edge = {
                    "source": step["component"],
                    "target": step["to"],
                    "label": flow.get("name", flow["id"]),
                    "flowId": flow["id"],
                    "flowType": flow_type,
                }
                edges.append(edge)
    return edges


def dedup_and_merge(flow_edges, dep_edges):
    """Remove dependency edges that overlap with flow edges.
    For bidirectional flow edges (A→B and B→A with same flowId),
    keep both arrows but hide the label on the return edge."""

    # Find flow pairs
    flow_pairs = set()
    for e in flow_edges:
        flow_pairs.add(tuple(sorted([e["source"], e["target"]])))

    # Drop overlapping dependency edges
    filtered_dep = []
    for e in dep_edges:
        pair = tuple(sorted([e["source"], e["target"]]))
        if pair not in flow_pairs:
            filtered_dep.append(e)

    # Handle bidirectional flow edges: keep both, hide label on return
    seen_directed = {}
    merged_flow = []
    for e in flow_edges:
        directed_key = (e["source"], e["target"], e["flowId"])
        reverse_key = (e["target"], e["source"], e["flowId"])

        if reverse_key in seen_directed:
            # This is the return edge — hide its label
            e["hideLabel"] = True
            e["label"] = ""

        seen_directed[directed_key] = True
        merged_flow.append(e)

    return merged_flow + filtered_dep


def extract_externals(arch, nodes):
    """Add external dependencies as nodes under an External group."""
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

    walk_components(arch.get("components", []), nodes, dep_edges)
    extract_externals(arch, nodes)

    # Support both v4 (flows) and legacy v3 (data_flows)
    raw_flows = arch.get("flows", arch.get("data_flows", []))
    flow_edges = extract_flow_edges(raw_flows)
    all_edges = dedup_and_merge(flow_edges, dep_edges)

    # State data (Data tab)
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

    # Failure modes (Resilience tab)
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

    # Flows (Flows tab) — typed
    flows = []
    for flow in raw_flows:
        flows.append({
            "id": flow["id"],
            "type": flow.get("type", "data"),
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
        "flows": flows,
    }


def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <atlas.json> <output.json>")
        sys.exit(1)

    with open(sys.argv[1]) as f:
        arch = yaml.safe_load(f)

    result = convert(arch)

    with open(sys.argv[2], "w") as f:
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

    flow_ids = set(e["flowId"] for e in edges if e["flowId"] not in ("dependency", "rendering"))
    bidir = sum(1 for e in edges if e.get("hideLabel"))

    # Count by flow type
    type_counts = {}
    for flow in result["flows"]:
        ft = flow.get("type", "data")
        type_counts[ft] = type_counts.get(ft, 0) + 1
    type_summary = ", ".join(f"{v} {k}" for k, v in sorted(type_counts.items()))

    print(f"Nodes: {len(nodes)} ({len(roots)} roots, {len(groups)} groups)")
    print(f"Edges: {len(edges)} ({len(flow_ids)} flows, {bidir} return edges with hidden labels)")
    print(f"Orphan leaves: {len(orphans)} (connected by containment)")
    print(f"State: {len(result['state'])}")
    print(f"Failure modes: {len(result['failure_modes'])}")
    print(f"Flows: {len(result['flows'])} ({type_summary})")
    print(f"Written to {sys.argv[2]}")


if __name__ == "__main__":
    main()
