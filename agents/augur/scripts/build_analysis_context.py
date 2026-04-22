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
    derived_dir = run_dir / "derived"
    startup_path = run_dir / "startup.json"
    blast_path = run_dir / "blast.json"
    atlas_path = run_dir / "atlas.json"
    stories_dir = run_dir / "stories"
    narratives_path = run_dir / "narratives.yaml"
    meta_path = run_dir / "meta.json"
    concepts_path = facts_dir / "concepts.json"
    story_seeds_path = derived_dir / "story-seeds.json"
    component_seeds_path = derived_dir / "component-seeds.json"
    narrative_seeds_path = derived_dir / "narrative-seeds.json"
    health_candidates_path = facts_dir / "health-candidates.json"
    failure_scenario_candidates_path = facts_dir / "failure-scenario-candidates.json"
    symbols_seed_path = facts_dir / "symbols-seed.json"
    state_seeds_path = facts_dir / "state-seeds.json"
    index_path = run_dir / "index.json"

    starter_files: list[str] = [str(blast_path), str(startup_path)]
    if index_path.exists():
        starter_files.append(str(index_path))
    try:
        startup = json.loads(startup_path.read_text(encoding="utf-8"))
        startup_files = startup.get("startup_files") or []
        if isinstance(startup_files, list):
            for relative_path in startup_files:
                if not isinstance(relative_path, str) or not relative_path.strip():
                    continue
                normalized = relative_path.removeprefix("./")
                absolute_path = run_dir / normalized
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
                "Read starter_files first and treat startup.json as the startup authority for this run.",
                "Use index.json as the canonical manifest and retrieval guide for deterministic and derived artifacts in this run.",
                "Use those core startup files to form initial hypotheses, then move into repo code before doing more fact reduction.",
                "Do not preload large supporting domains during startup. Read them only when the changed slice, a concrete ambiguity, or a review question requires them.",
                "Use larger supporting domains only when they help resolve ambiguity, answer review questions, or resolve materially relevant concept candidates.",
                "Preserve unchanged accepted outputs unless blast evidence forces wider revision.",
            ]
        )
    else:
        startup_directive = " ".join(
            [
                "Begin with the prepared analysis artifacts, not generic repo orientation.",
                "Read starter_files first and treat startup.json as the startup authority for this run.",
                "Use index.json as the canonical manifest and retrieval guide for deterministic and derived artifacts in this run.",
                "Use those core startup files to form initial architectural hypotheses, then move into repo code before doing more fact reduction.",
                "Do not preload large supporting domains during startup. Read them only when the current task actually needs them.",
                "Use larger supporting domains only when they help resolve ambiguity, answer review questions, or resolve materially relevant concept candidates.",
                "After you identify provisional top-level components, perform a mandatory breadth pass in repo code for each root slice.",
                "Use targeted fact domains on demand: concepts for concept questions, seeds for decomposition and narrative selection, and health or failure candidates for health, monitoring, or failure modeling.",
                "Perform a root challenge pass before finalizing roots: reject provisional roots anchored mainly in test/, docs/, examples/, or client-only paths.",
                "If the repo has strong engine, storage, or runtime slices, do not spend a full top-level root on bootstrap alone; keep bootstrap as a child unless it is truly the dominant system concern.",
                "On large repos, require at least one top-level root anchored in deeper runtime or storage internals when deterministic seeds provide one.",
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
        "derived_dir": str(derived_dir),
        "startup_path": str(startup_path),
        "blast_path": str(blast_path),
        "index_path": str(index_path),
        "concepts_path": str(concepts_path),
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
