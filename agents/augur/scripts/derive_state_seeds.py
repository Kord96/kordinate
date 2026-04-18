#!/usr/bin/env python3
"""Derive deterministic state-writing seeds from prepared facts and symbol seeds."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


STATE_NAME_HINTS = (
    ("db", "database"),
    ("database", "database"),
    ("sqlite", "database"),
    ("mysql", "database"),
    ("postgres", "database"),
    ("pg", "database"),
    ("storage", "storage"),
    ("store", "storage"),
    ("record", "records"),
    ("cdr", "records"),
    ("route", "routing"),
    ("trunk", "routing"),
    ("queue", "queueing"),
    ("session", "session"),
    ("ownership", "session"),
    ("config", "config"),
    ("acl", "policy"),
    ("cache", "cache"),
    ("map", "in-memory"),
)
STATE_TYPE_HINTS = (
    "struct",
    "enum",
    "type",
    "interface",
    "constant",
)
NOISY_PATH_PARTS = {"test", "tests", "__tests__", "spec", "specs", "docs", "examples", "example", "static"}
STATE_FILE_HINTS = ("db", "database", "storage", "store", "record", "cdr", "config", "model", "proxy/data", "gateway", "server")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Derive Augur state seeds from deterministic facts")
    parser.add_argument("facts_dir", help="facts/ directory for the prepared run")
    parser.add_argument("--output", required=True, help="Output JSON path")
    return parser.parse_args()


def normalize_fact_path(path: str) -> str:
    match = re.match(r"^(.*?):(\d+)$", path.strip())
    return match.group(1) if match else path.strip()


def infer_state_labels(path: str, symbols: list[dict[str, Any]]) -> list[str]:
    labels: list[str] = []
    lowered = path.lower()
    for token, label in STATE_NAME_HINTS:
        if token in lowered and label not in labels:
            labels.append(label)
    for symbol in symbols:
        name = str(symbol.get("name") or "").lower()
        for token, label in STATE_NAME_HINTS:
            if token in name and label not in labels:
                labels.append(label)
    return labels[:4]


def is_noisy_path(path: str) -> bool:
    path = normalize_fact_path(path)
    lowered = path.lower()
    parts = {part.lower() for part in Path(path).parts}
    return bool(parts & NOISY_PATH_PARTS) or lowered.endswith("_test.rs") or lowered.endswith(".test.js") or lowered.endswith(".spec.js")


def looks_stateful(path: str, exact_names: list[str]) -> bool:
    lowered = path.lower()
    if any(hint in lowered for hint in STATE_FILE_HINTS):
        return True
    for name in exact_names:
        lname = name.lower()
        if any(hint in lname for hint, _ in STATE_NAME_HINTS):
            return True
    return False


def load_source_lines(repo_root: Path, file_path: str) -> list[str]:
    try:
        return (repo_root / normalize_fact_path(file_path)).read_text(encoding="utf-8", errors="ignore").splitlines()
    except OSError:
        return []


def collect_line_refs_and_terms(lines: list[str], exact_names: list[str]) -> tuple[list[str], list[str]]:
    refs: list[str] = []
    terms: list[str] = []
    for idx, line in enumerate(lines, start=1):
        stripped = line.strip()
        if not stripped:
            continue
        matched = False
        for name in exact_names:
            if name and name in line:
                refs.append(f"{idx}")
                candidate = stripped[:180]
                if candidate not in terms:
                    terms.append(candidate)
                matched = True
                break
        if matched and len(refs) >= 6:
            break
    return refs[:6], terms[:6]


def main() -> int:
    args = parse_args()
    facts_dir = Path(args.facts_dir).resolve()
    output_path = Path(args.output).resolve()

    index_payload = load_json(facts_dir / "index.json") if (facts_dir / "index.json").exists() else {}
    repo_root = Path(str(index_payload.get("root") or "")).resolve() if index_payload.get("root") else None
    symbols_payload = load_json(facts_dir / "symbols-seed.json") if (facts_dir / "symbols-seed.json").exists() else {}
    component_payload = load_json(facts_dir / "component-seeds.json") if (facts_dir / "component-seeds.json").exists() else {}
    component_by_file: dict[str, str] = {}
    component_state_files: set[str] = set()
    for component in component_payload.get("candidate_components") or []:
        component_id = str(component.get("id") or "").strip()
        for bucket in ("representative_files", "entry_files", "flow_files", "state_or_ops_files"):
            for file_path in component.get(bucket) or []:
                if isinstance(file_path, str):
                    normalized = normalize_fact_path(file_path)
                    if normalized not in component_by_file:
                        component_by_file[normalized] = component_id
                    if bucket == "state_or_ops_files":
                        component_state_files.add(normalized)

    symbols_by_file: dict[str, list[dict[str, Any]]] = {}
    for symbol_entry in symbols_payload.get("files") or []:
        if not isinstance(symbol_entry, dict):
            continue
        file_path = normalize_fact_path(str(symbol_entry.get("file") or "").strip())
        if not file_path:
            continue
        symbols_by_file[file_path] = list(symbol_entry.get("symbols") or [])

    candidate_files: list[str] = []
    for file_path in component_state_files:
        if file_path and not is_noisy_path(file_path):
            candidate_files.append(file_path)
    for file_path in symbols_by_file:
        if file_path and not is_noisy_path(file_path) and file_path not in candidate_files:
            candidate_files.append(file_path)

    seeds: list[dict[str, Any]] = []
    for file_path in candidate_files:
        symbols = [symbol for symbol in symbols_by_file.get(file_path, []) if str(symbol.get("kind") or "") in STATE_TYPE_HINTS]
        if not symbols:
            symbols = list(symbols_by_file.get(file_path, []))[:8]
        exact_names = [str(symbol.get("name")) for symbol in symbols if isinstance(symbol.get("name"), str)]
        if not looks_stateful(file_path, exact_names) and file_path not in component_state_files:
            continue
        line_refs: list[str] = []
        preferred_claim_terms: list[str] = []
        if repo_root and repo_root.exists():
            source_lines = load_source_lines(repo_root, file_path)
            if source_lines:
                raw_refs, preferred_claim_terms = collect_line_refs_and_terms(source_lines, exact_names)
                if raw_refs:
                    line_refs = [f"{file_path}:{ref}" for ref in raw_refs]
                if not preferred_claim_terms:
                    for idx, line in enumerate(source_lines, start=1):
                        stripped = line.strip()
                        if not stripped:
                            continue
                        if any(hint in stripped.lower() for hint in STATE_FILE_HINTS):
                            line_refs.append(f"{file_path}:{idx}")
                            preferred_claim_terms.append(stripped[:180])
                        if len(preferred_claim_terms) >= 6:
                            break
                if not line_refs and preferred_claim_terms:
                    line_refs = [f"{file_path}:{idx}" for idx, line in enumerate(source_lines, start=1) if line.strip() in preferred_claim_terms[:6]][:6]
        seeds.append(
            {
                "file": file_path,
                "component_seed_id": component_by_file.get(file_path, ""),
                "state_labels": infer_state_labels(file_path, symbols),
                "exact_identifiers": exact_names[:12],
                "preferred_claim_terms": preferred_claim_terms,
                "line_refs": line_refs,
                "grounding_hint": (
                    "Prefer these exact identifiers when describing state in this file; keep one concrete storage or runtime mechanism per claim."
                ),
            }
        )

    payload = {
        "version": 1,
        "goal": "Advisory exact-name seeds for state entries grounded in state or operations files.",
        "planning_rules": [
            "When a state entry is grounded in one of these files, use exact identifiers from this inventory instead of abstract store paraphrases when possible.",
            "Prefer one concrete storage, config, queue, session, or snapshot mechanism per claim.",
            "Treat these seeds as a targeted state-writing aid, not as a complete storage model.",
        ],
        "files": seeds,
        "questions": [
            "Which exact structs, enums, types, maps, or config variants should appear in the state claim?",
            "Is the current state wording too abstract compared with the identifiers in the grounded file?",
            "Does one state claim mix multiple mechanisms that should be described separately?",
        ],
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
