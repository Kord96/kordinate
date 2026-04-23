"""Discover project context and load fact artifacts used by validation.

Checks owned here:
- derive the repo root for evidence/path checks
- verify that `facts/`, `observations/`, and `derived/` exist and are directories when needed
- load fact, observation, and planning JSON files used by downstream validators
- report JSON parse errors for those artifacts

This module does not validate atlas, stories, narratives, or meta contracts.
"""

import json
import os
from pathlib import Path


def derive_project_root(analysis_dir: Path) -> Path | None:
    explicit_project_root = os.environ.get("AUGUR_PROJECT_ROOT", "").strip()
    if explicit_project_root:
        explicit_candidate = Path(explicit_project_root)
        if explicit_candidate.exists():
            return explicit_candidate

    if "projects" not in analysis_dir.parts:
        return None

    proj_idx = analysis_dir.parts.index("projects")
    if proj_idx + 1 >= len(analysis_dir.parts):
        return None

    project_name = analysis_dir.parts[proj_idx + 1]
    configured_root = os.environ.get("PROJECTS_ROOT", "").strip()
    candidate_roots = []
    if configured_root:
        candidate_roots.append(Path(configured_root))
    candidate_roots.extend([Path("/kord/shared/repos"), Path("/kord/repos")])

    seen_roots: set[Path] = set()
    for projects_root in candidate_roots:
        if projects_root in seen_roots:
            continue
        seen_roots.add(projects_root)
        candidate = projects_root / project_name
        if candidate.exists():
            return candidate
    return None


def load_json_artifact(path: Path, section: str, issues: list[dict]) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError as exc:
        issues.append(
            {
                "level": "ERROR",
                "section": section,
                "message": f"JSON parse error: {exc}",
            }
        )
        return {}


def collect_facts_context(analysis_dir: Path, issues: list[dict]) -> dict:
    facts_dir = analysis_dir / "facts"
    observations_dir = analysis_dir / "observations"
    derived_dir = analysis_dir / "derived"
    if not facts_dir.exists():
        issues.append(
            {
                "level": "ERROR",
                "section": "structure",
                "message": f"facts/ directory not found at {facts_dir}. Write deterministic fact outputs here.",
            }
        )
    elif not facts_dir.is_dir():
        issues.append(
            {
                "level": "ERROR",
                "section": "structure",
                "message": f"facts path exists but is not a directory: {facts_dir}",
            }
        )

    if observations_dir.exists() and not observations_dir.is_dir():
        issues.append(
            {
                "level": "ERROR",
                "section": "structure",
                "message": f"observations path exists but is not a directory: {observations_dir}",
            }
        )

    if derived_dir.exists() and not derived_dir.is_dir():
        issues.append(
            {
                "level": "ERROR",
                "section": "structure",
                "message": f"derived path exists but is not a directory: {derived_dir}",
            }
        )

    payloads = {
        "concepts_payload": load_json_artifact(facts_dir / "concepts.json", "concepts", issues),
        "concept_observations_payload": load_json_artifact(observations_dir / "concepts.json", "concept-observations", issues),
        "frameworks_payload": load_json_artifact(facts_dir / "frameworks.json", "frameworks", issues),
        "component_observations_payload": load_json_artifact(observations_dir / "components.json", "component-observations", issues),
        "component_seeds_payload": load_json_artifact(derived_dir / "component-seeds.json", "component-seeds", issues),
        "story_observations_payload": load_json_artifact(observations_dir / "stories.json", "story-observations", issues),
        "story_seeds_payload": load_json_artifact(derived_dir / "story-seeds.json", "story-seeds", issues),
        "symbols_seed_payload": load_json_artifact(facts_dir / "symbols-seed.json", "symbols-seed", issues),
        "narrative_observations_payload": load_json_artifact(observations_dir / "narratives.json", "narrative-observations", issues),
        "narrative_seeds_payload": load_json_artifact(derived_dir / "narrative-seeds.json", "narrative-seeds", issues),
        "health_observations_payload": load_json_artifact(observations_dir / "health.json", "health-observations", issues),
        "health_candidates_payload": load_json_artifact(facts_dir / "health-candidates.json", "health-candidates", issues),
        "failure_observations_payload": load_json_artifact(observations_dir / "failure-scenarios.json", "failure-observations", issues),
        "control_hotspots_payload": load_json_artifact(facts_dir / "control-hotspots.json", "control-hotspots", issues),
        "state_access_summary_payload": load_json_artifact(
            facts_dir / "state-access-summary.json", "state-access-summary", issues
        ),
    }

    story_seed_refs: list[str] = []
    story_seeds_payload = payloads["story_seeds_payload"]
    if story_seeds_payload:
        raw_story_seed_refs = [
            *[str(item) for item in (story_seeds_payload.get("starter_files") or []) if item],
            *[str(item) for item in (story_seeds_payload.get("hot_files") or []) if item],
        ]
        seen_story_seed_refs: set[str] = set()
        for ref in raw_story_seed_refs:
            normalized = str(ref).split(":", 1)[0].strip()
            if normalized and normalized not in seen_story_seed_refs:
                seen_story_seed_refs.add(normalized)
                story_seed_refs.append(normalized)

    grounded_symbol_names: set[str] = set()
    symbols_seed_payload = payloads["symbols_seed_payload"]
    for file_entry in (symbols_seed_payload.get("files") or []) if isinstance(symbols_seed_payload, dict) else []:
        if not isinstance(file_entry, dict):
            continue
        for symbol in file_entry.get("symbols") or []:
            if not isinstance(symbol, dict):
                continue
            name = str(symbol.get("name") or "").strip()
            if name:
                grounded_symbol_names.add(name)

    payloads["story_seed_refs"] = story_seed_refs
    payloads["grounded_symbol_names"] = grounded_symbol_names
    payloads["facts_dir"] = facts_dir
    payloads["observations_dir"] = observations_dir
    payloads["derived_dir"] = derived_dir
    return payloads
