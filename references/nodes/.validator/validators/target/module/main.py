#!/usr/bin/env python3
"""Validate the node system layout."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
NODE_ID = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
REQUIRED_NODE_SECTIONS = (
    "Boundary",
    "Positive Evidence",
    "Rejections",
    "Edge Semantics",
    "Module Checks",
)


def issue(level: str, path: Path, message: str) -> dict[str, str]:
    return {"level": level, "path": str(path), "message": message}


def frontmatter(text: str) -> dict[str, str]:
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---", 4)
    if end < 0:
        return {}
    values: dict[str, str] = {}
    for line in text[4:end].splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            values[key.strip()] = value.strip()
    return values


def has_heading(text: str, heading: str) -> bool:
    return f"\n## {heading}\n" in text or text.startswith(f"## {heading}\n")


def check_node(node_dir: Path) -> list[dict[str, str]]:
    issues: list[dict[str, str]] = []
    if not NODE_ID.fullmatch(node_dir.name):
        issues.append(issue("ERROR", node_dir, "node directory must be kebab-case"))
    node_doc = node_dir / "NODE.md"
    legacy_semantics = node_dir / "semantics.md"
    if legacy_semantics.exists():
        issues.append(issue("ERROR", legacy_semantics, "use NODE.md; semantics.md is stale in the node design"))
    if not node_doc.is_file():
        issues.append(issue("ERROR", node_doc, "missing NODE.md"))
    else:
        text = node_doc.read_text(encoding="utf-8")
        metadata = frontmatter(text)
        if metadata.get("schema") != "node-system.v1":
            issues.append(issue("ERROR", node_doc, "NODE.md frontmatter must set schema: node-system.v1"))
        if metadata.get("node_id") != node_dir.name:
            issues.append(issue("ERROR", node_doc, "node_id must match the directory name"))
        for field in ("name", "summary", "detection_style", "detection_effort", "abstraction_level"):
            if field not in metadata:
                issues.append(issue("ERROR", node_doc, f"missing frontmatter field `{field}`"))
        for heading in REQUIRED_NODE_SECTIONS:
            if not has_heading(text, heading):
                issues.append(issue("ERROR", node_doc, f"missing `## {heading}` section"))
    module_main = node_dir / "module" / "main.py"
    if not module_main.is_file():
        issues.append(issue("ERROR", module_main, "missing node module entrypoint"))
    return issues


def main() -> int:
    issues: list[dict[str, str]] = []
    for required in (
        ROOT / "README.md",
        ROOT / "SCHEMA.md",
        ROOT / "module" / "README.md",
        ROOT / "nodes" / "SCHEMA.md",
        ROOT / "nodes" / "README.md",
    ):
        if not required.is_file():
            issues.append(issue("ERROR", required, "missing required node system file"))
    nodes_root = ROOT / "nodes"
    if nodes_root.is_dir():
        for child in sorted(nodes_root.iterdir()):
            if child.is_dir():
                issues.extend(check_node(child))
    else:
        issues.append(issue("ERROR", nodes_root, "missing nodes implementation directory"))
    errors = sum(1 for item in issues if item["level"] == "ERROR")
    warnings = sum(1 for item in issues if item["level"] == "WARNING")
    payload = {
        "valid": errors == 0,
        "status": "error" if errors else "warning" if warnings else "success",
        "errors": errors,
        "warnings": warnings,
        "issues": issues,
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if errors == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
