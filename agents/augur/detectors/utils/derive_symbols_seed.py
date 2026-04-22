#!/usr/bin/env python3
"""Derive deterministic exact-symbol seeds from high-signal repo files."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "detectors"))

from utils import detector_metadata_from_record, fact_payload, make_entity_ref, normalize_fact_record


SOURCE_DOMAINS = (
    "hot-files",
    "routes",
    "handlers",
    "dispatch-bindings",
    "boundaries",
    "jobs",
    "events",
    "external-clients",
    "config",
    "models",
)
MAX_FILES = 32
MAX_SYMBOLS_PER_FILE = 32
NOISY_PATH_PARTS = {"test", "tests", "__tests__", "spec", "specs", "docs", "examples", "example", "benchmark", "benchmarks"}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Derive Augur symbol seeds from deterministic facts")
    parser.add_argument("facts_dir", help="facts/ directory for the prepared run")
    parser.add_argument("--output", required=True, help="Output JSON path")
    return parser.parse_args()


def detect_language(path: str) -> str | None:
    suffix = Path(path).suffix.lower()
    return {
        ".py": "python",
        ".js": "javascript",
        ".cjs": "javascript",
        ".mjs": "javascript",
        ".ts": "typescript",
        ".tsx": "typescript",
        ".jsx": "javascript",
        ".go": "go",
        ".java": "java",
        ".rs": "rust",
    }.get(suffix)


def is_noisy_path(path: str) -> bool:
    parts = {part.lower() for part in Path(path).parts}
    if parts & NOISY_PATH_PARTS:
        return True
    lowered = path.lower()
    return lowered.endswith(".test.js") or lowered.endswith(".spec.js") or lowered.endswith("_test.go")


def add_symbol(results: list[dict[str, Any]], seen: set[tuple[str, str]], name: str, kind: str, exported: bool) -> None:
    normalized = name.strip()
    if not normalized:
        return
    key = (normalized, kind)
    if key in seen:
        return
    seen.add(key)
    results.append({"name": normalized, "kind": kind, "exported": exported})


def extract_python_symbols(text: str) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    for match in re.finditer(r"^\s*class\s+([A-Za-z_][A-Za-z0-9_]*)\b", text, re.MULTILINE):
        add_symbol(results, seen, match.group(1), "class", True)
    for match in re.finditer(r"^\s*(?:async\s+def|def)\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(", text, re.MULTILINE):
        name = match.group(1)
        if not name.startswith("_"):
            add_symbol(results, seen, name, "function", True)
    for match in re.finditer(r"^\s*([A-Z][A-Z0-9_]+)\s*=", text, re.MULTILINE):
        add_symbol(results, seen, match.group(1), "constant", True)
    return results


def extract_js_symbols(text: str) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    patterns = [
        (r"\bexport\s+default\s+class\s+([A-Za-z_$][A-Za-z0-9_$]*)\b", "class", True),
        (r"\bexport\s+class\s+([A-Za-z_$][A-Za-z0-9_$]*)\b", "class", True),
        (r"\bclass\s+([A-Za-z_$][A-Za-z0-9_$]*)\b", "class", True),
        (r"\bexport\s+interface\s+([A-Za-z_$][A-Za-z0-9_$]*)\b", "interface", True),
        (r"\binterface\s+([A-Za-z_$][A-Za-z0-9_$]*)\b", "interface", False),
        (r"\bexport\s+type\s+([A-Za-z_$][A-Za-z0-9_$]*)\b", "type", True),
        (r"\bexport\s+(?:async\s+)?function\s+([A-Za-z_$][A-Za-z0-9_$]*)\s*\(", "function", True),
        (r"\b(?:async\s+)?function\s+([A-Za-z_$][A-Za-z0-9_$]*)\s*\(", "function", True),
        (r"\bexport\s+const\s+([A-Za-z_$][A-Za-z0-9_$]*)\s*=", "constant", True),
        (r"\b(?:const|let|var)\s+([A-Za-z_$][A-Za-z0-9_$]*)\s*=\s*(?:async\s*)?function\b", "function", False),
        (r"\b(?:const|let|var)\s+([A-Za-z_$][A-Za-z0-9_$]*)\s*=\s*(?:async\s*)?(?:\([^)]*\)|[A-Za-z_$][A-Za-z0-9_$]*)\s*=>", "function", False),
        (r"\bconst\s+([A-Z][A-Z0-9_$]*)\s*=", "constant", False),
    ]
    for pattern, kind, exported in patterns:
        for match in re.finditer(pattern, text):
            add_symbol(results, seen, match.group(1), kind, exported)
    return results


def extract_go_symbols(text: str) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    for match in re.finditer(r"^\s*type\s+([A-Za-z_][A-Za-z0-9_]*)\s+(?:struct|interface)\b", text, re.MULTILINE):
        name = match.group(1)
        add_symbol(results, seen, name, "type", name[:1].isupper())
    for match in re.finditer(r"^\s*func\s+(?:\([^)]*\)\s*)?([A-Za-z_][A-Za-z0-9_]*)\s*\(", text, re.MULTILINE):
        name = match.group(1)
        add_symbol(results, seen, name, "function", name[:1].isupper())
    for match in re.finditer(r"^\s*(?:const|var)\s+([A-Za-z_][A-Za-z0-9_]*)\b", text, re.MULTILINE):
        name = match.group(1)
        add_symbol(results, seen, name, "binding", name[:1].isupper())
    return results


def extract_java_symbols(text: str) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    for match in re.finditer(r"\b(?:class|interface|enum|record)\s+([A-Z][A-Za-z0-9_]*)\b", text):
        add_symbol(results, seen, match.group(1), "type", True)
    method_pattern = re.compile(
        r"^\s*(?:public|protected|private)\s+(?:static\s+)?(?:final\s+)?(?:synchronized\s+)?[\w<>\[\], ?]+\s+([a-zA-Z_][A-Za-z0-9_]*)\s*\(",
        re.MULTILINE,
    )
    for match in method_pattern.finditer(text):
        add_symbol(results, seen, match.group(1), "method", True)
    for match in re.finditer(r"^\s*(?:public|protected|private)\s+static\s+final\s+[\w<>\[\], ?]+\s+([A-Z][A-Z0-9_]*)\b", text, re.MULTILINE):
        add_symbol(results, seen, match.group(1), "constant", True)
    return results


def extract_rust_symbols(text: str) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    patterns = [
        (r"\bpub\s+struct\s+([A-Za-z_][A-Za-z0-9_]*)\b", "struct", True),
        (r"\bstruct\s+([A-Za-z_][A-Za-z0-9_]*)\b", "struct", False),
        (r"\bpub\s+enum\s+([A-Za-z_][A-Za-z0-9_]*)\b", "enum", True),
        (r"\benum\s+([A-Za-z_][A-Za-z0-9_]*)\b", "enum", False),
        (r"\bpub\s+trait\s+([A-Za-z_][A-Za-z0-9_]*)\b", "trait", True),
        (r"\btrait\s+([A-Za-z_][A-Za-z0-9_]*)\b", "trait", False),
        (r"\bpub\s+fn\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(", "function", True),
        (r"\bfn\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(", "function", False),
    ]
    for pattern, kind, exported in patterns:
        for match in re.finditer(pattern, text):
            add_symbol(results, seen, match.group(1), kind, exported)
    return results


def extract_symbols(path: Path, language: str) -> list[dict[str, Any]]:
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return []

    if language == "python":
        symbols = extract_python_symbols(text)
    elif language in {"javascript", "typescript"}:
        symbols = extract_js_symbols(text)
    elif language == "go":
        symbols = extract_go_symbols(text)
    elif language == "java":
        symbols = extract_java_symbols(text)
    elif language == "rust":
        symbols = extract_rust_symbols(text)
    else:
        symbols = []
    return symbols[:MAX_SYMBOLS_PER_FILE]


def collect_candidate_files(facts_dir: Path) -> dict[str, dict[str, Any]]:
    candidates: dict[str, dict[str, Any]] = {}

    def note(path: str, reason: str, score: int) -> None:
        normalized = path.strip()
        if not normalized:
            return
        entry = candidates.setdefault(normalized, {"score": 0, "reasons": set()})
        entry["score"] += score
        entry["reasons"].add(reason)

    component_path = derived_dir / "component-seeds.json"
    if component_path.exists():
        payload = load_json(component_path)
        for component in payload.get("candidate_components") or []:
            component_id = str(component.get("id") or "").strip()
            for bucket in ("representative_files", "entry_files", "flow_files", "state_or_ops_files"):
                for path in component.get(bucket) or []:
                    if isinstance(path, str):
                        note(path, f"component-seed:{component_id or bucket}", 5 if bucket == "representative_files" else 4)

    for domain in SOURCE_DOMAINS:
        path = facts_dir / f"{domain}.json"
        if not path.exists():
            continue
        payload = load_json(path)
        entries = payload.get("facts") or payload.get("hot_files") or []
        for item in entries[:24]:
            if not isinstance(item, dict):
                continue
            raw = fact_payload(item)
            if isinstance(raw.get("file"), str):
                score = int(raw.get("score") or raw.get("fan_in") or 2)
                note(raw["file"], domain, max(1, min(score, 8)))
            for source in item.get("source_files") or []:
                if isinstance(source, str):
                    note(source.split(":")[0], domain, 2)
    return candidates


def main() -> int:
    args = parse_args()
    facts_dir = Path(args.facts_dir).resolve()
    output_path = Path(args.output).resolve()
    run_dir = facts_dir.parent
    derived_dir = run_dir / "derived"

    index_payload = load_json(run_dir / "index.json") if (run_dir / "index.json").exists() else {}
    repo_root = Path(str(index_payload.get("root") or "")).resolve() if index_payload.get("root") else None
    if not repo_root or not repo_root.exists():
        raise SystemExit("unable to resolve repo root from run index.json")

    candidates = collect_candidate_files(facts_dir)
    ranked_files = sorted(candidates.items(), key=lambda item: (-int(item[1]["score"]), item[0]))[:MAX_FILES]
    ranked_files = [item for item in ranked_files if not is_noisy_path(item[0])]

    file_entries: list[dict[str, Any]] = []
    symbol_index: dict[str, list[str]] = {}
    for rel_path, meta in ranked_files:
        language = detect_language(rel_path)
        if not language:
            continue
        full_path = repo_root / rel_path
        if not full_path.exists() or not full_path.is_file():
            continue
        symbols = extract_symbols(full_path, language)
        if not symbols:
            continue
        symbol_names = [str(symbol.get("name")) for symbol in symbols if isinstance(symbol.get("name"), str)]
        symbol_index[rel_path] = symbol_names
        file_entries.append({
            "file": rel_path,
            "language": language,
            "score": int(meta["score"]),
            "reasons": sorted(meta["reasons"]),
            "symbols": symbols,
        })

    component_hints: list[dict[str, Any]] = []
    component_path = derived_dir / "component-seeds.json"
    if component_path.exists():
        component_payload = load_json(component_path)
        for component in component_payload.get("candidate_components") or []:
            component_id = str(component.get("id") or "").strip()
            files = [path for path in (component.get("representative_files") or []) if isinstance(path, str)]
            notable: list[str] = []
            for path in files:
                for symbol in symbol_index.get(path, [])[:8]:
                    if symbol not in notable:
                        notable.append(symbol)
            component_hints.append({
                "component_seed_id": component_id,
                "representative_files": files[:3],
                "notable_symbols": notable[:12],
            })

    normalized_facts = [
        normalize_fact_record({
            "id": stable_id(entry["file"], "symbols"),
            "kind": "symbols-seed",
            "domain": "symbols-seed",
            "summary": f"Exact symbol inventory for {entry['file']}",
            "source_files": [entry["file"]],
            "raw_evidence": {**entry, "confidence_hint": "high"},
            "relationships": [
                relation
                for relation in (
                    make_entity_ref("component", str(component_id), "grounded_in_component")
                    for component_id in (entry.get("component_ids") or [])
                )
                if relation
            ],
        })
        for entry in file_entries
    ]
    detectors: dict[str, dict[str, Any]] = {}
    for fact in normalized_facts:
        metadata = detector_metadata_from_record(fact)
        detectors[str(metadata.get("id") or "")] = metadata
        fact.pop("domain", None)

    payload = {
        "version": 1,
        "domain": "symbols-seed",
        "detectors": detectors,
        "goal": "Advisory exact-symbol inventory for high-signal files and component slices.",
        "count": len(normalized_facts),
        "facts": normalized_facts,
        "planning_rules": [
            "Use these symbols to prefer exact mechanism names over abstract paraphrases when writing findings, summaries, and flow steps.",
            "Treat this as a deterministic name dictionary for high-signal files, not as a complete repo-wide symbol index.",
            "If a claim names a hook, parser, registry, option, command, stage, or class, prefer an exact symbol from this inventory when one exists.",
        ],
        "files": file_entries,
        "component_symbol_hints": component_hints,
        "questions": [
            "Which exact identifiers from these files should appear in observations instead of abstract paraphrases?",
            "Which representative files expose the mechanism names that anchor each top-level component?",
            "Which grounding warnings can be fixed by replacing vague stage descriptions with exact symbol names from this inventory?",
        ],
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
