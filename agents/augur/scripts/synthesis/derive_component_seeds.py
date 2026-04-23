#!/usr/bin/env python3
"""Derive deterministic component-reading seeds from prepared fact artifacts."""

from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any


COMMON_CONTAINER_DIRS = {"pkg", "internal", "src", "apps", "cmd", "lib", "services", "modules"}
ENTRY_HINTS = ("main", "cmd", "server", "app", "bootstrap", "root", "cli", "start", "run")
FLOW_HINTS = ("handler", "route", "api", "server", "scan", "watch", "sync", "worker", "job", "process", "exec")
STATE_HINTS = ("store", "repo", "sql", "db", "cache", "config", "state", "model", "driver", "client", "adapter", "metrics")
NOISY_PATH_PARTS = {"test", "tests", "__tests__", "docs", "examples", "example", "spec", "specs", "benchmark", "benchmarks"}
ROOT_LIKELIHOOD_HINTS = (
    ("pkg/vm", 8),
    ("pkg/sql", 8),
    ("pkg/frontend", 7),
    ("pkg/tnservice", 8),
    ("pkg/logservice", 8),
    ("pkg/fileservice", 7),
    ("pkg/cnservice", 8),
    ("pkg/txn", 7),
    ("src/proxy", 6),
    ("src/rwi", 5),
)
ROOT_DEMOTION_HINTS = (
    ("cmd/", -5),
    ("clients/", -6),
    ("test/", -8),
    ("tests/", -8),
    ("docs/", -8),
    ("examples/", -7),
)
SEED_SOURCE_DOMAINS = (
    "hot-files",
    "boundaries",
    "routes",
    "handlers",
    "dispatch-bindings",
    "registrations",
    "jobs",
    "events",
    "external-clients",
    "config",
    "models",
)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Derive Augur component seeds from deterministic facts")
    parser.add_argument("facts_dir", help="facts/ directory for the prepared run")
    parser.add_argument("--output", required=True, help="Output JSON path")
    return parser.parse_args()


def slugify(text: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return slug or "root"


def normalize_fact_path(path: str) -> str:
    match = re.match(r"^(.*?):(\d+)$", path.strip())
    return match.group(1) if match else path.strip()


def group_key_for_file(path: str) -> str:
    path = normalize_fact_path(path)
    parts = [part for part in Path(path).parts if part not in {".", ""}]
    if not parts:
        return "root"
    if len(parts) >= 2 and parts[0] in COMMON_CONTAINER_DIRS:
        return "/".join(parts[:2])
    return parts[0]


def is_noisy_path(path: str) -> bool:
    path = normalize_fact_path(path)
    parts = {part.lower() for part in Path(path).parts}
    lowered = path.lower()
    if parts & NOISY_PATH_PARTS:
        return True
    return lowered.endswith(".test.js") or lowered.endswith(".spec.js") or lowered.endswith("_test.go") or lowered.endswith("_test.rs")


def file_score(record: dict[str, Any]) -> int:
    raw = record.get("raw_evidence") or {}
    return int(raw.get("score") or raw.get("fan_in") or 1)


def candidate_files_from_payload(domain: str, payload: dict[str, Any]) -> list[dict[str, Any]]:
    entries = payload.get("facts") or payload.get("hot_files") or []
    candidates: list[dict[str, Any]] = []
    for item in entries:
        if not isinstance(item, dict):
            continue
        files: list[str] = []
        raw = item.get("raw_evidence") or {}
        raw_file = raw.get("file")
        if isinstance(raw_file, str) and raw_file.strip():
            files.append(raw_file.strip())
        for source_file in item.get("source_files") or []:
            if isinstance(source_file, str) and source_file.strip():
                files.append(source_file.strip())
        score = file_score(item)
        for path in dict.fromkeys(files):
            path = normalize_fact_path(path)
            if is_noisy_path(path):
                continue
            candidates.append(
                {
                    "path": path,
                    "domain": domain,
                    "score": score,
                    "summary": str(item.get("summary") or ""),
                }
            )
    return candidates


def classify_role(path: str) -> str:
    path = normalize_fact_path(path)
    lowered = path.lower()
    name = Path(path).stem.lower()
    if any(token in lowered or token in name for token in ENTRY_HINTS):
        return "entry"
    if any(token in lowered or token in name for token in STATE_HINTS):
        return "state"
    if any(token in lowered or token in name for token in FLOW_HINTS):
        return "flow"
    return "support"


def best_file(candidates: list[dict[str, Any]], role: str) -> str | None:
    matching = [candidate for candidate in candidates if classify_role(candidate["path"]) == role]
    if matching:
        matching.sort(key=lambda item: (-item["score"], item["path"]))
        return matching[0]["path"]
    if candidates:
        sorted_candidates = sorted(candidates, key=lambda item: (-item["score"], item["path"]))
        return sorted_candidates[0]["path"]
    return None


def short_rationale(group: str, candidates: list[dict[str, Any]]) -> str:
    domains = sorted({candidate["domain"] for candidate in candidates})
    if not domains:
        return f"Representative deterministic slice around {group}."
    return f"Representative deterministic slice around {group}, surfaced by {', '.join(domains[:4])}."


def root_likelihood(group: str, files: list[dict[str, Any]]) -> int:
    score = 0
    lowered_group = group.lower()
    for hint, delta in ROOT_LIKELIHOOD_HINTS:
        if hint in lowered_group:
            score += delta
    for path, delta in ROOT_DEMOTION_HINTS:
        if path in lowered_group:
            score += delta
    signals = {candidate["domain"] for candidate in files}
    if signals <= {"hot-files", "models"}:
        score -= 6
    if any(classify_role(candidate["path"]) in {"entry", "flow"} for candidate in files):
        score += 4
    stateful = sum(1 for candidate in files if classify_role(candidate["path"]) == "state")
    score += min(stateful, 2)
    return score


def main() -> int:
    args = parse_args()
    facts_dir = Path(args.facts_dir).resolve()
    output_path = Path(args.output).resolve()

    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for domain in SEED_SOURCE_DOMAINS:
        domain_path = facts_dir / f"{domain}.json"
        if not domain_path.exists():
            continue
        try:
            payload = load_json(domain_path)
        except json.JSONDecodeError:
            continue
        for candidate in candidate_files_from_payload(domain, payload):
            grouped[group_key_for_file(candidate["path"])].append(candidate)

    component_seeds: list[dict[str, Any]] = []
    scored_groups: list[tuple[int, int, str, list[dict[str, Any]]]] = []
    for group, candidates in grouped.items():
        deduped_for_score: dict[str, dict[str, Any]] = {}
        for candidate in candidates:
            existing = deduped_for_score.get(candidate["path"])
            if existing is None or candidate["score"] > existing["score"]:
                deduped_for_score[candidate["path"]] = candidate
        files = list(deduped_for_score.values())
        files.sort(key=lambda item: (-item["score"], item["path"]))
        entry_file = best_file(files, "entry")
        flow_file = best_file(files, "flow")
        if not entry_file and not flow_file:
            continue
        raw_score = sum(candidate["score"] for candidate in files)
        scored_groups.append((-(raw_score + root_likelihood(group, files)), -raw_score, group, files))

    ranked_groups = scored_groups[:]
    ranked_groups.sort(key=lambda item: (item[0], item[1], item[2]))
    ranked_groups = ranked_groups[:8]

    for _, _, group, files in ranked_groups:
        entry_file = best_file(files, "entry")
        flow_file = best_file(files, "flow")
        state_file = best_file(files, "state")
        representative_files = [path for path in dict.fromkeys([entry_file, flow_file, state_file]) if path]

        component_seeds.append(
            {
                "id": slugify(group.replace("/", "-")),
                "group": group,
                "rationale": short_rationale(group, files),
                "signals": sorted({candidate["domain"] for candidate in files}),
                "root_likelihood": root_likelihood(group, files),
                "representative_files": representative_files[:3],
                "entry_files": [entry_file] if entry_file else [],
                "flow_files": [flow_file] if flow_file else [],
                "state_or_ops_files": [state_file] if state_file else [],
            }
        )

    payload = {
        "version": 1,
        "goal": "Advisory component-level reading seeds for full-mode semantic breadth passes.",
        "planning_rules": [
            "Treat these seeds as candidate slices for breadth-first repo reading, not final component truth.",
            "For each accepted top-level component, read at least one representative entry file, one flow file, and one state or operations file when available.",
            "Merge or discard seeds that do not correspond to real runtime or ownership boundaries.",
        ],
        "candidate_components": component_seeds,
        "questions": [
            "Which candidate slices correspond to real top-level runtime or ownership boundaries?",
            "Which representative files should be read to validate each provisional component before writing stories?",
            "Which seeds are only support code and should stay inside a broader parent component?",
        ],
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
