#!/usr/bin/env python3
"""Prepare deterministic Augur analysis artifacts in a run directory.

This is the shared entrypoint for the pre-semantic stage. It materializes:
- facts/*.json via extract_facts.py
- facts/concept-evidence.json via infer_concepts_from_facts.py
- blast.json via compute_blast_radius.py
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Prepare deterministic Augur artifacts in a run dir")
    parser.add_argument("repo_root", help="Repository root to analyze")
    parser.add_argument("--run-dir", required=True, help="Prepared analysis run directory")
    parser.add_argument("--project", required=True, help="Project slug")
    parser.add_argument("--agent-home", required=True, help="Agent home directory for blast computation")
    parser.add_argument("--current-sha", help="Optional current commit SHA to forward to blast computation")
    parser.add_argument("--previous-sha", help="Optional previous commit SHA to forward to blast computation")
    parser.add_argument(
        "--analysis-mode",
        choices=["full", "incremental", "design"],
        default="full",
        help="Deterministic analysis mode label",
    )
    parser.add_argument("--pretty", action="store_true", help="Pretty-print generated JSON files")
    return parser.parse_args()


def run_cmd(args: list[str]) -> None:
    result = subprocess.run(args, check=False, capture_output=True, text=True)
    if result.returncode == 0:
        return
    if result.stdout:
        sys.stderr.write(result.stdout)
    if result.stderr:
        sys.stderr.write(result.stderr)
    raise subprocess.CalledProcessError(result.returncode, args)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def upsert_domain_record(domains: list[dict], name: str, file: str, count: int) -> list[dict]:
    updated = [
        domain for domain in domains
        if str(domain.get("name") or "") != name
    ]
    updated.append({
        "name": name,
        "file": file,
        "count": count,
    })
    updated.sort(key=lambda item: str(item.get("name") or ""))
    return updated


def refresh_fact_manifests(
    facts_dir: Path,
    concept_evidence_path: Path,
    story_seeds_path: Path,
    component_seeds_path: Path,
    narrative_seeds_path: Path,
    health_candidates_path: Path,
    failure_scenario_candidates_path: Path,
    symbols_seed_path: Path,
    state_seeds_path: Path,
) -> None:
    domain_records: list[tuple[str, str, int]] = []
    if concept_evidence_path.exists():
        concept_payload = load_json(concept_evidence_path)
        concept_count = int(concept_payload.get("count") or len(concept_payload.get("facts") or []))
        domain_records.append(("concept-evidence", "facts/concept-evidence.json", concept_count))
    if story_seeds_path.exists():
        story_payload = load_json(story_seeds_path)
        story_count = int(len(story_payload.get("candidate_concern_classes") or []))
        domain_records.append(("story-seeds", "facts/story-seeds.json", story_count))
    if component_seeds_path.exists():
        component_payload = load_json(component_seeds_path)
        component_count = int(len(component_payload.get("candidate_components") or []))
        domain_records.append(("component-seeds", "facts/component-seeds.json", component_count))
    if narrative_seeds_path.exists():
        narrative_payload = load_json(narrative_seeds_path)
        system_overview = narrative_payload.get("system_overview") or {}
        narrative_count = int(len(system_overview.get("preferred_root_components") or []))
        domain_records.append(("narrative-seeds", "facts/narrative-seeds.json", narrative_count))
    if health_candidates_path.exists():
        health_payload = load_json(health_candidates_path)
        health_count = int(
            len(health_payload.get("local_candidates") or [])
            + len(health_payload.get("integration_candidates") or [])
            + len(health_payload.get("propagation_candidates") or [])
        )
        domain_records.append(("health-candidates", "facts/health-candidates.json", health_count))
    if failure_scenario_candidates_path.exists():
        failure_scenario_payload = load_json(failure_scenario_candidates_path)
        failure_scenario_count = int(len(failure_scenario_payload.get("candidates") or []))
        domain_records.append(("failure-scenario-candidates", "facts/failure-scenario-candidates.json", failure_scenario_count))
    if symbols_seed_path.exists():
        symbols_payload = load_json(symbols_seed_path)
        symbols_count = int(len(symbols_payload.get("files") or []))
        domain_records.append(("symbols-seed", "facts/symbols-seed.json", symbols_count))
    if state_seeds_path.exists():
        state_payload = load_json(state_seeds_path)
        state_count = int(len(state_payload.get("files") or []))
        domain_records.append(("state-seeds", "facts/state-seeds.json", state_count))
    if not domain_records:
        return

    index_path = facts_dir / "index.json"
    if index_path.exists():
        index_payload = load_json(index_path)
        index = index_payload.setdefault("index", {})
        domains = index.setdefault("domains", [])
        for name, file, count in domain_records:
            domains = upsert_domain_record(domains, name, file, count)
        index["domains"] = domains
        write_json(index_path, index_payload)

    startup_path = facts_dir / "startup.json"
    if startup_path.exists():
        startup_payload = load_json(startup_path)
        large_domains = startup_payload.get("large_domains") or []
        for name, file, count in domain_records:
            large_domains = upsert_domain_record(large_domains, name, file, count)
        startup_payload["large_domains"] = large_domains

        domain_counts = startup_payload.get("domain_counts") or []
        for name, file, count in domain_records:
            domain_counts = upsert_domain_record(domain_counts, name, file, count)
        startup_payload["domain_counts"] = domain_counts
        write_json(startup_path, startup_payload)


def main() -> int:
    args = parse_args()
    repo_root = Path(args.repo_root).resolve()
    run_dir = Path(args.run_dir).resolve()
    facts_dir = run_dir / "facts"
    concept_evidence_path = facts_dir / "concept-evidence.json"
    story_seeds_path = facts_dir / "story-seeds.json"
    component_seeds_path = facts_dir / "component-seeds.json"
    narrative_seeds_path = facts_dir / "narrative-seeds.json"
    health_candidates_path = facts_dir / "health-candidates.json"
    failure_scenario_candidates_path = facts_dir / "failure-scenario-candidates.json"
    symbols_seed_path = facts_dir / "symbols-seed.json"
    state_seeds_path = facts_dir / "state-seeds.json"
    facts_guide_path = facts_dir / "facts-guide.json"
    blast_path = run_dir / "blast.json"

    run_dir.mkdir(parents=True, exist_ok=True)
    facts_dir.mkdir(parents=True, exist_ok=True)

    extract_cmd = [
        "python3",
        str(ROOT / "scripts" / "extract_facts.py"),
        str(repo_root),
        "--output-dir",
        str(facts_dir),
        "--analysis-mode",
        args.analysis_mode,
    ]
    if args.pretty:
        extract_cmd.append("--pretty")
    run_cmd(extract_cmd)

    run_cmd([
        "python3",
        str(ROOT / "scripts" / "infer_concepts_from_facts.py"),
        str(facts_dir),
        "--output",
        str(concept_evidence_path),
    ])
    run_cmd([
        "python3",
        str(ROOT / "scripts" / "derive_story_seeds.py"),
        str(facts_dir),
        "--output",
        str(story_seeds_path),
    ])
    run_cmd([
        "python3",
        str(ROOT / "scripts" / "derive_component_seeds.py"),
        str(facts_dir),
        "--output",
        str(component_seeds_path),
    ])
    run_cmd([
        "python3",
        str(ROOT / "scripts" / "derive_narrative_seeds.py"),
        str(facts_dir),
        "--output",
        str(narrative_seeds_path),
    ])
    run_cmd([
        "python3",
        str(ROOT / "scripts" / "derive_health_candidates.py"),
        str(facts_dir),
        "--output",
        str(health_candidates_path),
    ])
    run_cmd([
        "python3",
        str(ROOT / "scripts" / "derive_failure_scenario_candidates.py"),
        str(facts_dir),
        "--output",
        str(failure_scenario_candidates_path),
    ])
    run_cmd([
        "python3",
        str(ROOT / "scripts" / "derive_symbols_seed.py"),
        str(facts_dir),
        "--output",
        str(symbols_seed_path),
    ])
    run_cmd([
        "python3",
        str(ROOT / "scripts" / "derive_state_seeds.py"),
        str(facts_dir),
        "--output",
        str(state_seeds_path),
    ])
    refresh_fact_manifests(
        facts_dir,
        concept_evidence_path,
        story_seeds_path,
        component_seeds_path,
        narrative_seeds_path,
        health_candidates_path,
        failure_scenario_candidates_path,
        symbols_seed_path,
        state_seeds_path,
    )
    run_cmd([
        "python3",
        str(ROOT / "scripts" / "build_facts_guide.py"),
        str(facts_dir),
        "--output",
        str(facts_guide_path),
    ])

    blast_cmd = [
        "python3",
        str(ROOT / "scripts" / "compute_blast_radius.py"),
        str(repo_root),
        "--project",
        args.project,
        "--agent-home",
        str(Path(args.agent_home).resolve()),
        "--output",
        str(blast_path),
    ]
    if args.current_sha:
        blast_cmd.extend(["--current-sha", args.current_sha])
    if args.previous_sha:
        blast_cmd.extend(["--previous-sha", args.previous_sha])
    run_cmd(blast_cmd)

    payload = {
        "repo_root": str(repo_root),
        "run_dir": str(run_dir),
        "facts_dir": str(facts_dir),
        "concept_evidence": str(concept_evidence_path),
        "story_seeds": str(story_seeds_path),
        "component_seeds": str(component_seeds_path),
        "narrative_seeds": str(narrative_seeds_path),
        "health_candidates": str(health_candidates_path),
        "symbols_seed": str(symbols_seed_path),
        "state_seeds": str(state_seeds_path),
        "facts_guide": str(facts_guide_path),
        "blast": str(blast_path),
        "analysis_mode": args.analysis_mode,
    }
    print(json.dumps(payload))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
