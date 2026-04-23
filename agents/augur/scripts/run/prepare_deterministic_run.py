#!/usr/bin/env python3
"""Prepare deterministic Augur analysis artifacts in a run directory.

This is the shared entrypoint for the pre-semantic stage. It materializes:
- facts/*.json normalized deterministic evidence via extract_facts.py and detector follow-on scripts
- observations/*.json normalized semantic assessment aids via observation builders
- root manifests (`startup.json`, `index.json`) via extract_facts.py
- derived/*.json semantic planning aids via derive scripts
- blast.json via compute_blast_radius.py
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


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
    run_dir: Path,
    facts_dir: Path,
    concepts_path: Path,
    concept_observations_path: Path,
    health_observations_path: Path,
    failure_observations_path: Path,
    component_observations_path: Path,
    story_observations_path: Path,
    narrative_observations_path: Path,
    story_seeds_path: Path,
    component_seeds_path: Path,
    narrative_seeds_path: Path,
    health_candidates_path: Path,
    failure_scenario_candidates_path: Path,
    symbols_seed_path: Path,
    state_seeds_path: Path,
) -> None:
    fact_records: list[tuple[str, str, int]] = []
    observation_records: list[tuple[str, str, int]] = []
    derived_records: list[tuple[str, str, int]] = []
    if concepts_path.exists():
        concept_payload = load_json(concepts_path)
        concept_count = int(concept_payload.get("count") or len(concept_payload.get("facts") or []))
        fact_records.append(("concepts", "facts/concepts.json", concept_count))
    if concept_observations_path.exists():
        observation_payload = load_json(concept_observations_path)
        observation_count = int(observation_payload.get("count") or len(observation_payload.get("observations") or []))
        observation_records.append(("concepts", "observations/concepts.json", observation_count))
    if health_observations_path.exists():
        payload = load_json(health_observations_path)
        observation_records.append(("health", "observations/health.json", int(payload.get("count") or len(payload.get("observations") or []))))
    if failure_observations_path.exists():
        payload = load_json(failure_observations_path)
        observation_records.append(("failure-scenarios", "observations/failure-scenarios.json", int(payload.get("count") or len(payload.get("observations") or []))))
    if component_observations_path.exists():
        payload = load_json(component_observations_path)
        observation_records.append(("components", "observations/components.json", int(payload.get("count") or len(payload.get("observations") or []))))
    if story_observations_path.exists():
        payload = load_json(story_observations_path)
        observation_records.append(("stories", "observations/stories.json", int(payload.get("count") or len(payload.get("observations") or []))))
    if narrative_observations_path.exists():
        payload = load_json(narrative_observations_path)
        observation_records.append(("narratives", "observations/narratives.json", int(payload.get("count") or len(payload.get("observations") or []))))
    if story_seeds_path.exists():
        story_payload = load_json(story_seeds_path)
        story_count = int(len(story_payload.get("candidate_concern_classes") or []))
        derived_records.append(("story-seeds", "derived/story-seeds.json", story_count))
    if component_seeds_path.exists():
        component_payload = load_json(component_seeds_path)
        component_count = int(len(component_payload.get("candidate_components") or []))
        derived_records.append(("component-seeds", "derived/component-seeds.json", component_count))
    if narrative_seeds_path.exists():
        narrative_payload = load_json(narrative_seeds_path)
        system_overview = narrative_payload.get("system_overview") or {}
        narrative_count = int(len(system_overview.get("preferred_root_components") or []))
        derived_records.append(("narrative-seeds", "derived/narrative-seeds.json", narrative_count))
    if health_candidates_path.exists():
        health_payload = load_json(health_candidates_path)
        health_count = int(health_payload.get("count") or len(health_payload.get("facts") or [])) or int(
            len(health_payload.get("local_candidates") or [])
            + len(health_payload.get("integration_candidates") or [])
            + len(health_payload.get("propagation_candidates") or [])
        )
        fact_records.append(("health-candidates", "facts/health-candidates.json", health_count))
    if failure_scenario_candidates_path.exists():
        failure_scenario_payload = load_json(failure_scenario_candidates_path)
        failure_scenario_count = int(failure_scenario_payload.get("count") or len(failure_scenario_payload.get("facts") or [])) or int(len(failure_scenario_payload.get("candidates") or []))
        fact_records.append(("failure-scenario-candidates", "facts/failure-scenario-candidates.json", failure_scenario_count))
    if symbols_seed_path.exists():
        symbols_payload = load_json(symbols_seed_path)
        symbols_count = int(symbols_payload.get("count") or len(symbols_payload.get("facts") or [])) or int(len(symbols_payload.get("files") or []))
        fact_records.append(("symbols-seed", "facts/symbols-seed.json", symbols_count))
    if state_seeds_path.exists():
        state_payload = load_json(state_seeds_path)
        state_count = int(state_payload.get("count") or len(state_payload.get("facts") or [])) or int(len(state_payload.get("files") or []))
        fact_records.append(("state-seeds", "facts/state-seeds.json", state_count))
    state_access_summary_path = facts_dir / "state-access-summary.json"
    if state_access_summary_path.exists():
        summary_payload = load_json(state_access_summary_path)
        summary_count = int(summary_payload.get("count") or len(summary_payload.get("facts") or [])) or int(len(summary_payload.get("components") or []))
        fact_records.append(("state-access-summary", "facts/state-access-summary.json", summary_count))
    control_hotspots_path = facts_dir / "control-hotspots.json"
    if control_hotspots_path.exists():
        hotspots_payload = load_json(control_hotspots_path)
        hotspot_count = int(len(hotspots_payload.get("facts") or []))
        fact_records.append(("control-hotspots", "facts/control-hotspots.json", hotspot_count))
    if not fact_records and not observation_records and not derived_records:
        return

    derived_dir = run_dir / "derived"
    derived_dir.mkdir(parents=True, exist_ok=True)
    move_map = {
        story_seeds_path: derived_dir / "story-seeds.json",
        component_seeds_path: derived_dir / "component-seeds.json",
        narrative_seeds_path: derived_dir / "narrative-seeds.json",
    }
    for old_path, new_path in move_map.items():
        if old_path.exists():
            old_path.replace(new_path)

    index_path = run_dir / "index.json"
    if index_path.exists():
        index_payload = load_json(index_path)
        domains = list((index_payload.get("index") or {}).get("domains") or [])
        for name, file, count in fact_records:
            domains = upsert_domain_record(domains, name, file, count)
        if isinstance(index_payload.get("index"), dict):
            index_payload["index"]["domains"] = domains
        index_payload["observation_artifacts"] = [
            {"name": name, "file": file, "count": count}
            for name, file, count in sorted(observation_records, key=lambda item: item[0])
        ]
        index_payload["derived_artifacts"] = [
            {"name": name, "file": file, "count": count}
            for name, file, count in sorted(derived_records, key=lambda item: item[0])
        ]
        index_payload["observations_root"] = "observations/"
        write_json(index_path, index_payload)

    startup_path = run_dir / "startup.json"
    if startup_path.exists():
        startup_payload = load_json(startup_path)
        targeted = startup_payload.get("targeted_domains")
        if isinstance(targeted, dict):
            targeted["concept_questions"] = [
                "observations/concepts.json",
                "facts/frameworks.json",
            ]
            targeted["decomposition_and_narratives"] = [
                "observations/components.json",
                "observations/stories.json",
                "observations/narratives.json",
            ]
            targeted["health_and_failure"] = [
                "observations/health.json",
                "observations/failure-scenarios.json",
                "facts/control-hotspots.json",
            ]
        startup_payload["observation_artifacts"] = [
            {"name": name, "file": file, "count": count}
            for name, file, count in sorted(observation_records, key=lambda item: item[0])
        ]
        startup_payload["derived_artifacts"] = [
            {"name": name, "file": file, "count": count}
            for name, file, count in sorted(derived_records, key=lambda item: item[0])
        ]
        write_json(startup_path, startup_payload)


def main() -> int:
    args = parse_args()
    repo_root = Path(args.repo_root).resolve()
    run_dir = Path(args.run_dir).resolve()
    facts_dir = run_dir / "facts"
    observations_dir = run_dir / "observations"
    derived_dir = run_dir / "derived"
    concepts_path = facts_dir / "concepts.json"
    concept_observations_path = observations_dir / "concepts.json"
    health_observations_path = observations_dir / "health.json"
    failure_observations_path = observations_dir / "failure-scenarios.json"
    component_observations_path = observations_dir / "components.json"
    story_observations_path = observations_dir / "stories.json"
    narrative_observations_path = observations_dir / "narratives.json"
    story_seeds_path = derived_dir / "story-seeds.json"
    component_seeds_path = derived_dir / "component-seeds.json"
    narrative_seeds_path = derived_dir / "narrative-seeds.json"
    health_candidates_path = facts_dir / "health-candidates.json"
    failure_scenario_candidates_path = facts_dir / "failure-scenario-candidates.json"
    symbols_seed_path = facts_dir / "symbols-seed.json"
    state_seeds_path = facts_dir / "state-seeds.json"
    blast_path = run_dir / "blast.json"
    index_path = run_dir / "index.json"
    startup_path = run_dir / "startup.json"

    run_dir.mkdir(parents=True, exist_ok=True)
    facts_dir.mkdir(parents=True, exist_ok=True)
    observations_dir.mkdir(parents=True, exist_ok=True)
    derived_dir.mkdir(parents=True, exist_ok=True)

    extract_cmd = [
        "python3",
        str(ROOT / "detectors" / "scripts" / "extract_facts.py"),
        str(repo_root),
        "--output-dir",
        str(facts_dir),
        "--output-root",
        str(run_dir),
        "--analysis-mode",
        args.analysis_mode,
    ]
    if args.pretty:
        extract_cmd.append("--pretty")
    run_cmd(extract_cmd)

    run_cmd([
        "python3",
        str(ROOT / "detectors" / "scripts" / "infer_concepts_from_facts.py"),
        str(facts_dir),
        "--output",
        str(concepts_path),
    ])
    run_cmd([
        "python3",
        str(ROOT / "detectors" / "scripts" / "derive_concept_observations.py"),
        str(concepts_path),
        "--output",
        str(concept_observations_path),
    ])
    run_cmd([
        "python3",
        str(ROOT / "scripts" / "synthesis" / "derive_story_seeds.py"),
        str(facts_dir),
        "--output",
        str(story_seeds_path),
    ])
    run_cmd([
        "python3",
        str(ROOT / "scripts" / "synthesis" / "derive_component_seeds.py"),
        str(facts_dir),
        "--output",
        str(component_seeds_path),
    ])
    run_cmd([
        "python3",
        str(ROOT / "detectors" / "scripts" / "derive_component_observations.py"),
        str(component_seeds_path),
        "--output",
        str(component_observations_path),
    ])
    run_cmd([
        "python3",
        str(ROOT / "scripts" / "synthesis" / "derive_narrative_seeds.py"),
        str(facts_dir),
        "--output",
        str(narrative_seeds_path),
    ])
    run_cmd([
        "python3",
        str(ROOT / "detectors" / "scripts" / "derive_narrative_observations.py"),
        str(narrative_seeds_path),
        "--output",
        str(narrative_observations_path),
    ])
    run_cmd([
        "python3",
        str(ROOT / "detectors" / "scripts" / "derive_story_observations.py"),
        str(story_seeds_path),
        "--output",
        str(story_observations_path),
    ])
    run_cmd([
        "python3",
        str(ROOT / "detectors" / "scripts" / "derive_health_candidates.py"),
        str(facts_dir),
        "--output",
        str(health_candidates_path),
    ])
    run_cmd([
        "python3",
        str(ROOT / "detectors" / "scripts" / "derive_health_observations.py"),
        str(health_candidates_path),
        "--output",
        str(health_observations_path),
    ])
    run_cmd([
        "python3",
        str(ROOT / "detectors" / "scripts" / "derive_failure_scenario_candidates.py"),
        str(facts_dir),
        "--output",
        str(failure_scenario_candidates_path),
    ])
    run_cmd([
        "python3",
        str(ROOT / "detectors" / "scripts" / "derive_failure_observations.py"),
        str(failure_scenario_candidates_path),
        "--output",
        str(failure_observations_path),
    ])
    run_cmd([
        "python3",
        str(ROOT / "detectors" / "scripts" / "derive_symbols_seed.py"),
        str(facts_dir),
        "--output",
        str(symbols_seed_path),
    ])
    run_cmd([
        "python3",
        str(ROOT / "detectors" / "scripts" / "derive_state_seeds.py"),
        str(facts_dir),
        "--output",
        str(state_seeds_path),
    ])
    refresh_fact_manifests(
        run_dir,
        facts_dir,
        concepts_path,
        concept_observations_path,
        health_observations_path,
        failure_observations_path,
        component_observations_path,
        story_observations_path,
        narrative_observations_path,
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
        str(ROOT / "scripts" / "run" / "enrich_facts_index.py"),
        str(run_dir),
    ])
    stale_facts_guide_path = run_dir / "facts-guide.json"
    if stale_facts_guide_path.exists():
        stale_facts_guide_path.unlink()

    blast_cmd = [
        "python3",
        str(ROOT / "scripts" / "run" / "compute_blast_radius.py"),
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
        "observations_dir": str(observations_dir),
        "derived_dir": str(derived_dir),
        "startup": str(startup_path),
        "concepts": str(concepts_path),
        "concept_observations": str(concept_observations_path),
        "health_observations": str(health_observations_path),
        "failure_observations": str(failure_observations_path),
        "component_observations": str(component_observations_path),
        "story_observations": str(story_observations_path),
        "narrative_observations": str(narrative_observations_path),
        "story_seeds": str(story_seeds_path),
        "component_seeds": str(component_seeds_path),
        "narrative_seeds": str(narrative_seeds_path),
        "health_candidates": str(health_candidates_path),
        "failure_scenario_candidates": str(failure_scenario_candidates_path),
        "symbols_seed": str(symbols_seed_path),
        "state_seeds": str(state_seeds_path),
        "index": str(index_path),
        "blast": str(blast_path),
        "analysis_mode": args.analysis_mode,
    }
    print(json.dumps(payload))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
