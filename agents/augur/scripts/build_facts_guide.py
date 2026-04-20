#!/usr/bin/env python3
"""Build a run-specific interpretation guide for deterministic fact artifacts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT / "schemas" / "facts-catalog.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build Augur facts guide for one run")
    parser.add_argument("facts_dir", help="facts directory for the run")
    parser.add_argument("--output", required=True, help="Output JSON path")
    return parser.parse_args()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    args = parse_args()
    facts_dir = Path(args.facts_dir).resolve()
    output_path = Path(args.output).resolve()
    catalog = load_json(CATALOG_PATH)
    catalog_artifacts = catalog.get("artifacts", {}) or {}
    index_payload = load_json(facts_dir / "index.json") if (facts_dir / "index.json").exists() else {}
    startup_payload = load_json(facts_dir / "startup.json") if (facts_dir / "startup.json").exists() else {}

    startup_files = {
        str(item).removeprefix("facts/").removesuffix(".json")
        for item in (startup_payload.get("startup_files") or [])
        if isinstance(item, str)
    }

    entries: list[dict[str, Any]] = []
    seen: set[str] = set()

    def default_meaning(name: str, kind: str) -> str:
        if kind == "observation-domain":
            return f"Normalized deterministic observations for the '{name}' domain."
        if kind == "planning-aid":
            return f"Deterministic planning aid for '{name}'."
        if kind == "derived-structure":
            return f"Deterministic derived structure for '{name}'."
        return f"Deterministic {kind} artifact for '{name}'."

    def default_how_to_use(name: str, kind: str) -> str:
        if kind == "observation-domain":
            return f"Use '{name}' as supporting evidence when it helps clarify components, flows, state, or dependencies."
        if kind == "planning-aid":
            return f"Use '{name}' to refine planning or prioritization before final semantic writing."
        if kind == "derived-structure":
            return f"Use '{name}' as a deterministic summary to guide follow-up repo reads and architectural checks."
        return f"Use '{name}' according to its run-specific role before wider repo exploration."

    def default_what_not_to_infer(kind: str) -> str:
        if kind == "observation-domain":
            return "Do not treat one observation domain as final architecture truth without corroborating code reads."
        if kind == "planning-aid":
            return "Do not treat this planning aid as a final semantic conclusion."
        if kind == "derived-structure":
            return "Do not treat this derived summary as a substitute for direct code grounding."
        return "Do not over-interpret this artifact without corroborating evidence."

    def add_entry(name: str, file: str, count: int | None = None) -> None:
        if name in seen:
            return
        seen.add(name)
        catalog_entry = catalog_artifacts.get(name, {})
        kind = catalog_entry.get("kind", "observation-domain")
        entries.append({
            "name": name,
            "file": file,
            "kind": kind,
            "priority": (
                "startup" if name in startup_files else catalog_entry.get("priority", "targeted-disambiguation")
            ),
            "count": count,
            "meaning": catalog_entry.get("meaning", default_meaning(name, kind)),
            "how_to_use": catalog_entry.get("how_to_use", default_how_to_use(name, kind)),
            "what_not_to_infer": catalog_entry.get("what_not_to_infer", default_what_not_to_infer(kind)),
        })

    add_entry("index", "facts/index.json")
    add_entry("startup", "facts/startup.json")

    for domain in (index_payload.get("index", {}) or {}).get("domains", []) or []:
        name = str(domain.get("name") or "").strip()
        file = str(domain.get("file") or f"facts/{name}.json")
        count = domain.get("count")
        if name:
            add_entry(name, file, int(count) if isinstance(count, int) else count)

    for extra_name, entry in catalog_artifacts.items():
        file = str(entry.get("file") or "")
        if not file:
            continue
        candidate = facts_dir.parent / file if file.startswith("facts/") else facts_dir / file
        if candidate.exists():
            add_entry(extra_name, file)

    payload = {
        "version": 1,
        "goal": "Run-specific interpretation guide for deterministic Augur fact artifacts.",
        "read_order": [
            "facts/startup.json",
            "facts/facts-guide.json",
            "facts/index.json",
            "facts/concept-evidence.json",
            "facts/component-seeds.json",
            "facts/narrative-seeds.json",
            "facts/health-candidates.json",
            "facts/symbols-seed.json",
            "facts/state-seeds.json"
        ],
        "rules": [
            "Observation-domain files contain normalized observations and usually expose a top-level facts array.",
            "Planning-aid, guide, manifest, and derived-structure artifacts may use specialized JSON shapes and should not be forced into a facts-array interpretation.",
            "Treat concept-evidence as candidate guidance: resolve materially relevant concepts from supporting evidence, counter evidence, evidence gaps, review questions, and repo code before letting them affect atlas concepts, monitoring, or gaps.",
            "Deterministic artifacts are guidance and evidence, not final semantic conclusions.",
        ],
        "artifacts": entries,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
