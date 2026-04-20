#!/usr/bin/env python3
"""Build Augur semantic runtime context from prepared run artifacts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build Augur semantic runtime context")
    parser.add_argument("--project", required=True, help="Project name")
    parser.add_argument("--working-dir", required=True, help="Target repo working directory")
    parser.add_argument("--run-dir", required=True, help="Prepared semantic run directory")
    parser.add_argument("--analysis-mode", required=True, choices=["full", "incremental"], help="Prepared analysis mode")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    run_dir = Path(args.run_dir).resolve()
    analysis_dir = run_dir.parent
    project_mem = analysis_dir.parent
    facts_dir = run_dir / "facts"
    startup_path = facts_dir / "startup.json"
    blast_path = run_dir / "blast.json"
    atlas_path = run_dir / "atlas.json"
    stories_dir = run_dir / "stories"
    narratives_path = run_dir / "narratives.yaml"
    meta_path = run_dir / "meta.json"
    concept_evidence_path = facts_dir / "concept-evidence.json"
    story_seeds_path = facts_dir / "story-seeds.json"
    component_seeds_path = facts_dir / "component-seeds.json"
    narrative_seeds_path = facts_dir / "narrative-seeds.json"
    health_candidates_path = facts_dir / "health-candidates.json"
    failure_scenario_candidates_path = facts_dir / "failure-scenario-candidates.json"
    symbols_seed_path = facts_dir / "symbols-seed.json"
    state_seeds_path = facts_dir / "state-seeds.json"
    facts_guide_path = facts_dir / "facts-guide.json"

    starter_files: list[str] = [str(blast_path), str(startup_path)]
    for optional in (facts_guide_path, concept_evidence_path, story_seeds_path, component_seeds_path, narrative_seeds_path, health_candidates_path, failure_scenario_candidates_path, symbols_seed_path, state_seeds_path):
        if optional.exists():
            starter_files.append(str(optional))
    try:
        startup = json.loads(startup_path.read_text(encoding="utf-8"))
        startup_files = startup.get("startup_files") or []
        if isinstance(startup_files, list):
            for relative_path in startup_files:
                if not isinstance(relative_path, str) or not relative_path.strip():
                    continue
                normalized = relative_path.removeprefix("./")
                absolute_path = run_dir / normalized if normalized.startswith("facts/") else facts_dir / normalized
                absolute = str(absolute_path)
                if absolute not in starter_files:
                    starter_files.append(absolute)
    except Exception:
        for fallback in (
            facts_dir / "frameworks.json",
            facts_dir / "boundaries.json",
            facts_dir / "dispatch-bindings.json",
            facts_dir / "hot-files.json",
        ):
            absolute = str(fallback)
            if fallback.exists() and absolute not in starter_files:
                starter_files.append(absolute)

    if args.analysis_mode == "incremental":
        startup_directive = " ".join(
            [
                "Begin with the prepared analysis artifacts, not generic repo orientation.",
                "Read starter_files first and treat facts/startup.json plus facts/index.json as the authority for which deterministic domains are available in this run.",
                "Use those facts to form initial hypotheses, then move into repo code before doing more fact reduction.",
                "Use larger supporting domains only when they help resolve ambiguity, answer review questions, or resolve materially relevant concept candidates.",
                "Use facts/symbols-seed.json when present to prefer exact mechanism names from high-signal files over abstract paraphrases in observations and summaries.",
                "Use facts/state-seeds.json when present to tighten state claims around exact structs, enums, maps, config variants, or storage selectors in the grounded files.",
                "Preserve unchanged accepted outputs unless blast evidence forces wider revision.",
            ]
        )
    else:
        startup_directive = " ".join(
            [
                "Begin with the prepared analysis artifacts, not generic repo orientation.",
                "Read starter_files first and treat facts/startup.json plus facts/index.json as the authority for which deterministic domains are available in this run.",
                "Use those facts to form initial architectural hypotheses, then move into repo code before doing more fact reduction.",
                "Use larger supporting domains only when they help resolve ambiguity, answer review questions, or resolve materially relevant concept candidates.",
                "After you identify provisional top-level components, perform a mandatory breadth pass in repo code for each root slice.",
                "Treat facts/concept-evidence.json as candidate guidance: use supporting evidence, counter evidence, evidence gaps, and review questions to resolve concepts before they affect atlas concepts, monitoring, or gaps.",
                "Use facts/component-seeds.json when present to choose representative files for each provisional root slice before finalizing the atlas or stories.",
                "Use facts/narrative-seeds.json when present to challenge system-overview and other narrative selections before finalizing narratives.",
                "Use facts/health-candidates.json when present to challenge unit health criteria, shared failure-scenario links, top-level monitoring coverage, and top-level gaps before finalizing the atlas.",
                "Use facts/failure-scenario-candidates.json when present to challenge whether repeated multi-unit cascades should become a top-level failure_scenarios entry.",
                "Perform a root challenge pass before finalizing roots: reject provisional roots anchored mainly in test/, docs/, examples/, or client-only paths.",
                "If the repo has strong engine, storage, or runtime slices, do not spend a full top-level root on bootstrap alone; keep bootstrap as a child unless it is truly the dominant system concern.",
                "On large repos, require at least one top-level root anchored in deeper runtime or storage internals when deterministic seeds provide one.",
                "Use facts/symbols-seed.json when present to prefer exact mechanism names from high-signal files over abstract paraphrases in summaries, observations, and flows.",
                "Use facts/state-seeds.json when present to tighten state claims around exact structs, enums, maps, config variants, or storage selectors in the grounded files.",
                "For each provisional top-level component, inspect at least one composition or entry file, one primary behavior or flow file, and one state, dependency, or operations file before finalizing stories.",
                "Use facts to prioritize where to start, not to cap how broadly you read in full mode.",
                "Use the run manifest for available fact files instead of guessing optional paths.",
            ]
        )

    payload = {
        "project": args.project,
        "mode": args.analysis_mode,
        "working_dir": str(Path(args.working_dir).resolve()),
        "run_dir": str(run_dir),
        "analysis_dir": str(analysis_dir),
        "project_mem": str(project_mem),
        "facts_dir": str(facts_dir),
        "startup_path": str(startup_path),
        "blast_path": str(blast_path),
        "facts_guide_path": str(facts_guide_path),
        "concept_evidence_path": str(concept_evidence_path),
        "story_seeds_path": str(story_seeds_path),
        "component_seeds_path": str(component_seeds_path),
        "narrative_seeds_path": str(narrative_seeds_path),
        "health_candidates_path": str(health_candidates_path),
        "failure_scenario_candidates_path": str(failure_scenario_candidates_path),
        "symbols_seed_path": str(symbols_seed_path),
        "state_seeds_path": str(state_seeds_path),
        "atlas_path": str(atlas_path),
        "stories_dir": str(stories_dir),
        "narratives_path": str(narratives_path),
        "meta_path": str(meta_path),
        "latest_path": str(analysis_dir.parent / "latest.json"),
        "starter_files": starter_files,
        "startup_directive": startup_directive,
    }
    print(json.dumps(payload))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
