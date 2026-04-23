#!/usr/bin/env python3
"""Run one complete Augur validation pass for an analysis directory.

This module is the validator coordinator. It checks or dispatches checks for:
- required startup artifacts: `blast.json` and the `facts/` directory
- full-run artifacts when present: `atlas.json`, `stories/*.yaml`,
  `narratives.yaml`, and optional sealed `meta.json`
- cross-artifact consistency between atlas, stories, narratives, and facts
- append-only validation history in `log.json`
- final sealing for a clean full-artifact run
- terminal console summary, lock handling, and exit code

Detailed contract checks live in sibling modules:
- `atlas_model.py`: atlas structure, components, flows, state, dependencies,
  concepts, monitoring, failure scenarios, gaps, and optional domains
- `story.py`: story schema, anchor grounding, teaching quality, and atlas refs
- `narrative.py`: narrative schema and story-path consistency
- `meta.py`: sealed `meta.json` contract

Run modes:
- facts-only: requires only `blast.json` and `facts/`
- full-artifact: also validates atlas, stories, narratives, and sealed metadata
"""

import json
import os
import sys
from pathlib import Path

AUGUR_ROOT = Path(__file__).resolve().parents[3]
AUGUR_RUN_SCRIPTS_DIR = AUGUR_ROOT / "scripts" / "run"
if str(AUGUR_RUN_SCRIPTS_DIR) not in sys.path:
    sys.path.append(str(AUGUR_RUN_SCRIPTS_DIR))

from .constants import FACTS_ONLY_MODE, RUN_LOG_FILE
from .context import collect_facts_context, derive_project_root
from finalize_analysis import finalize_analysis_dir

from .helpers import load_yaml, path_matches_prefix
from .history import append_validation_history, load_validation_history
from .atlas_model import validate_atlas
from .meta import validate_meta
from .narrative import detect_cross_artifact_conflicts, validate_narrative
from .story import validate_story


def finalize_validation_run(
    analysis_dir: Path,
    run_log_path: Path,
    all_issues: list[dict],
) -> tuple[bool, str]:
    """Append the current validation result and optionally seal a clean run.

    Checks performed here:
    - append the current issue set to `log.json`
    - if the run is clean and not facts-only, invoke final sealing
    - re-validate generated `meta.json` after sealing
    - append a second invalid snapshot if sealing introduced new errors
    """

    errors = [issue for issue in all_issues if issue["level"] == "ERROR"]
    valid = len(errors) == 0

    append_validation_history(run_log_path, analysis_dir, valid, all_issues)
    validation_log = load_validation_history(run_log_path)
    latest_iteration = (validation_log.get("iterations") or [])[-1] if (validation_log.get("iterations") or []) else {}
    final_status = str(latest_iteration.get("status") or ("valid" if valid else "invalid"))

    if final_status == "valid" and not FACTS_ONLY_MODE:
        try:
            finalize_analysis_dir(
                analysis_dir,
                validation_token=os.environ.get("AUGUR_VALIDATION_TOKEN", "").strip(),
                validation_attempts=int(os.environ.get("AUGUR_VALIDATION_ATTEMPTS", "0") or "0"),
            )
            meta = json.loads((analysis_dir / "meta.json").read_text())
            if isinstance(meta, dict):
                all_issues.extend(validate_meta(meta, analysis_dir))
            else:
                all_issues.append(
                    {
                        "level": "ERROR",
                        "section": "meta",
                        "message": "meta.json must be a JSON object",
                    }
                )
        except Exception as exc:
            all_issues.append(
                {
                    "level": "ERROR",
                    "section": "meta",
                    "message": f"sealing failed: {exc}",
                }
            )

        errors = [issue for issue in all_issues if issue["level"] == "ERROR"]
        valid = len(errors) == 0
        if not valid:
            append_validation_history(run_log_path, analysis_dir, valid, all_issues)
            validation_log = load_validation_history(run_log_path)
            latest_iteration = (validation_log.get("iterations") or [])[-1] if (validation_log.get("iterations") or []) else {}
            final_status = str(latest_iteration.get("status") or "invalid")

    return valid, final_status


def print_summary_and_exit(
    analysis_dir: Path,
    use_lock: bool,
    lock_path: Path,
    all_issues: list[dict],
    valid: bool,
    final_status: str,
) -> None:
    """Print the final validation summary, update the lock, and exit.

    This function does not perform new validation checks. It only renders:
    - every accumulated issue
    - the final banner and counts
    - expected artifact structure hints for invalid runs
    - lock-file state when `VALIDATE_LOCK=1`
    """

    errors = [issue for issue in all_issues if issue["level"] == "ERROR"]
    warnings = [issue for issue in all_issues if issue["level"] == "WARNING"]

    for issue in all_issues:
        section = f" [{issue['section']}]" if issue.get("section") else ""
        print(f"{issue['level']}{section}: {issue['message']}")

    banner = "VALID" if final_status == "valid" else ("NEEDS_REFINEMENT" if final_status == "needs_refinement" else "INVALID")
    print(f"\n{banner}: {len(errors)} errors, {len(warnings)} warnings")

    if not valid:
        print(f"\nExpected output structure at {analysis_dir}:")
        print(f"  {analysis_dir}/blast.json           — deterministic blast radius JSON")
        print(f"  {analysis_dir}/facts/               — normalized fact domain files")
        if not FACTS_ONLY_MODE:
            print(f"  {analysis_dir}/atlas.json           — v4 JSON (see atlas-schema.md)")
            print(f"  {analysis_dir}/stories/*.yaml       — one YAML file per story")
            print(f"  {analysis_dir}/narratives.yaml      — cross-cutting story sequences")

    if use_lock:
        if final_status == "valid":
            if lock_path.exists():
                lock_path.unlink()
                print(f"Lock removed: {lock_path}")
        else:
            lock_path.write_text(f"{len(errors)} errors\n")
            print(f"Lock created: {lock_path}")

    sys.exit(0 if final_status == "valid" else 1)

def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <analysis-dir> [--lock]")
        sys.exit(2)

    analysis_dir = Path(sys.argv[1])
    use_lock = os.environ.get("VALIDATE_LOCK") == "1"
    lock_path = analysis_dir / ".validate-lock"
    run_log_path = analysis_dir / RUN_LOG_FILE

    if not analysis_dir.exists():
        print(f"Directory not found: {analysis_dir}")
        sys.exit(2)

    all_issues = []

    project_root = derive_project_root(analysis_dir)

    # --- Facts and script-derived artifacts ---
    blast_path = analysis_dir / "blast.json"
    if not blast_path.exists():
        all_issues.append({"level": "ERROR", "section": "structure", "message": f"blast.json not found at {blast_path}. Write blast radius output to this exact path."})
    else:
        try:
            json.loads(blast_path.read_text())
        except json.JSONDecodeError as e:
            all_issues.append({"level": "ERROR", "section": "blast", "message": f"JSON parse error: {e}"})

    facts_context = collect_facts_context(analysis_dir, all_issues)
    concepts_payload = facts_context["concepts_payload"]
    frameworks_payload = facts_context["frameworks_payload"]
    component_seeds_payload = facts_context["component_seeds_payload"]
    story_seeds_payload = facts_context["story_seeds_payload"]
    grounded_symbol_names = facts_context["grounded_symbol_names"]
    narrative_seeds_payload = facts_context["narrative_seeds_payload"]
    health_candidates_payload = facts_context["health_candidates_payload"]
    control_hotspots_payload = facts_context["control_hotspots_payload"]
    state_access_summary_payload = facts_context["state_access_summary_payload"]
    story_seed_refs = facts_context["story_seed_refs"]

    atlas_node_ids = set()
    atlas_entity_ids = set()
    atlas = {}
    if not FACTS_ONLY_MODE:
        # --- Atlas ---
        atlas_path = analysis_dir / "atlas.json"

        if not atlas_path.exists():
            all_issues.append({"level": "ERROR", "section": "structure", "message": f"atlas.json not found at {atlas_path}. Write your full architecture atlas to this exact path."})
        elif atlas_path.suffix != ".json":
            all_issues.append({"level": "ERROR", "section": "structure", "message": f"atlas should be .json, got {atlas_path.suffix}"})
        else:
            try:
                atlas = json.loads(atlas_path.read_text())
                issues, atlas_node_ids, atlas_entity_ids = validate_atlas(
                    atlas,
                    project_root,
                    analysis_dir,
                    concepts_payload,
                    frameworks_payload,
                    health_candidates_payload,
                )
                all_issues.extend(issues)
            except json.JSONDecodeError as e:
                all_issues.append({"level": "ERROR", "section": "atlas", "message": f"JSON parse error: {e}"})

        if atlas and component_seeds_payload:
            top_level_components = [
                component for component in (atlas.get("components") or [])
                if isinstance(component, dict) and not component.get("parent")
            ]
            for seed in component_seeds_payload.get("candidate_components") or []:
                if not isinstance(seed, dict):
                    continue
                root_likelihood = int(seed.get("root_likelihood") or 0)
                if root_likelihood < 6:
                    continue
                representative_files = [str(item) for item in (seed.get("representative_files") or []) if item]
                if not representative_files:
                    continue
                seed_id = str(seed.get("id") or "")
                group = str(seed.get("group") or seed_id or "seed")
                matched = False
                for component in top_level_components:
                    component_id = str(component.get("id") or "")
                    component_name = str(component.get("name") or "")
                    modules = [str(item) for item in (component.get("modules") or []) if item]
                    if seed_id and seed_id in {component_id, component_name.lower().replace(" ", "-")}:
                        matched = True
                        break
                    if any(path_matches_prefix(module, candidate) for module in modules for candidate in representative_files):
                        matched = True
                        break
                if not matched:
                    all_issues.append({
                        "level": "WARNING",
                        "section": "components",
                        "kind": "component-model",
                        "message": f"Strong script-derived component seed '{group}' is not clearly represented by a top-level component",
                        "related_entities": [seed_id] if seed_id else [],
                        "evidence_refs": representative_files[:3],
                        "conflict_type": "evidence_vs_model",
                    })

    story_ids = set()
    all_stories: dict[str, dict] = {}
    narratives: list[dict] = []
    if not FACTS_ONLY_MODE:
        component_signal_counts: dict[str, int] = {}
        atlas_story_node_details: dict[str, dict] = {}
        if isinstance(atlas, dict):
            component_ids = {
                str(component.get("id"))
                for component in (atlas.get("components") or [])
                if isinstance(component, dict) and component.get("id")
            }
            for component in atlas.get("components") or []:
                if isinstance(component, dict) and component.get("id"):
                    atlas_story_node_details[str(component.get("id"))] = {
                        "kind": "component",
                        "description": component.get("description"),
                        "summary": component.get("summary"),
                    }
            for dependency in atlas.get("external_dependencies") or []:
                if isinstance(dependency, dict) and dependency.get("id"):
                    atlas_story_node_details[str(dependency.get("id"))] = {
                        "kind": "external dependency",
                        "description": dependency.get("description"),
                        "summary": dependency.get("summary"),
                    }
            for flow in atlas.get("flows") or []:
                if not isinstance(flow, dict):
                    continue
                for step in flow.get("steps") or []:
                    if isinstance(step, dict):
                        component = str(step.get("component") or "")
                        if component in component_ids:
                            component_signal_counts[component] = component_signal_counts.get(component, 0) + 1
            for state in atlas.get("state") or []:
                if isinstance(state, dict):
                    component = str(state.get("component") or "")
                    if component in component_ids:
                        component_signal_counts[component] = component_signal_counts.get(component, 0) + 1
            for dependency in atlas.get("external_dependencies") or []:
                if not isinstance(dependency, dict):
                    continue
                for component in dependency.get("components") or []:
                    component = str(component or "")
                    if component in component_ids:
                        component_signal_counts[component] = component_signal_counts.get(component, 0) + 1

        # --- Stories ---
        stories_dir = analysis_dir / "stories"

        if not stories_dir.exists():
            all_issues.append({"level": "ERROR", "section": "structure", "message": f"stories/ directory not found at {stories_dir}. Write each story as a separate .yaml file in this directory."})
        else:
            for f in sorted(stories_dir.iterdir()):
                if f.suffix == ".md":
                    all_issues.append({"level": "ERROR", "section": "structure", "message": f"Story file is .md (should be .yaml): {f.name}"})
                    continue
                if f.suffix not in (".yaml", ".yml"):
                    continue
                story = load_yaml(f)
                if story is None:
                    all_issues.append({"level": "ERROR", "section": "story", "message": f"Failed to parse: {f.name}"})
                    continue
                sid = story.get("id", f.stem)
                story_ids.add(sid)
                all_issues.extend(validate_story(
                    story,
                    atlas_node_ids,
                    atlas_entity_ids,
                    grounded_symbol_names,
                    atlas_story_node_details,
                    project_root,
                    analysis_dir,
                ))

            # Story tree: check children per parent
            for f in sorted(stories_dir.iterdir()):
                if f.suffix not in (".yaml", ".yml"):
                    continue
                story = load_yaml(f)
                if story:
                    all_stories[story.get("id", f.stem)] = story

            children_count = {}
            for sid, story in all_stories.items():
                parent = story.get("parent")
                if parent:
                    children_count[parent] = children_count.get(parent, 0) + 1

            for parent_id, count in children_count.items():
                if count > 5:
                    all_issues.append({"level": "ERROR", "section": "story",
                        "message": f"Story '{parent_id}' has {count} children (max 5). Consolidate child stories."})
                elif count < 2:
                    all_issues.append({
                        "level": "WARNING",
                        "section": "story",
                        "kind": "story-decomposition",
                        "message": f"Story '{parent_id}' has {count} child (preferred 2+). Add another distinct concern or merge the child back into the parent.",
                        "related_entities": [parent_id],
                        "evidence_refs": story_seed_refs[:3],
                    })
                if count < 2 and component_signal_counts.get(parent_id, 0) >= 4:
                    all_issues.append({
                        "level": "WARNING",
                        "section": "story",
                        "kind": "story-decomposition",
                        "message": f"Story '{parent_id}' looks under-decomposed for a root with multiple flows/state/dependencies. Draft more concern-focused children before finalizing.",
                        "related_entities": [parent_id],
                        "evidence_refs": story_seed_refs[:3],
                        "conflict_type": "evidence_vs_model" if story_seed_refs else None,
                    })

            root_story_count = sum(1 for story in all_stories.values() if not story.get("parent"))
            if root_story_count < 3:
                all_issues.append({"level": "ERROR", "section": "story",
                    "message": f"Too few root stories: {root_story_count} (minimum 3, one per top-level component)"})
            elif root_story_count > 5:
                all_issues.append({"level": "ERROR", "section": "story",
                    "message": f"Too many root stories: {root_story_count} (maximum 5, one per top-level component)"})

            if all_stories and not children_count and len(all_stories) >= 4:
                all_issues.append({
                    "level": "ERROR",
                    "section": "story",
                    "kind": "story-decomposition",
                    "message": "Story tree is fully flat. Add child stories when root stories contain distinct nested concerns.",
                    "related_entities": sorted(all_stories.keys()),
                    "evidence_refs": story_seed_refs[:3],
                    "conflict_type": "evidence_vs_model" if story_seed_refs else None,
                })

        # --- Narratives ---
        narratives_path = analysis_dir / "narratives.yaml"
        if not narratives_path.exists():
            all_issues.append({"level": "ERROR", "section": "structure", "message": f"narratives.yaml not found at {narratives_path}. Write cross-cutting story sequences here."})
        else:
            narratives_doc = load_yaml(narratives_path)
            if narratives_doc is None:
                all_issues.append({"level": "ERROR", "section": "narrative", "message": f"Failed to parse: {narratives_path.name}"})
            else:
                if not isinstance(narratives_doc, dict):
                    all_issues.append({"level": "ERROR", "section": "narrative", "message": "narratives.yaml must be a mapping with top-level version and narratives keys"})
                    narratives = []
                else:
                    version = narratives_doc.get("version")
                    if version != "1":
                        all_issues.append({"level": "ERROR", "section": "narrative", "message": f"narratives.yaml version must be '1', got '{version}'"})
                    narratives = narratives_doc.get("narratives", [])
                if not isinstance(narratives, list):
                    all_issues.append({"level": "ERROR", "section": "narrative", "message": "narratives.yaml must contain a top-level 'narratives' list"})
                else:
                    ids = set()
                    child_story_ids = {sid for sid, story in all_stories.items() if story.get("parent")}
                    if len(narratives) < 2:
                        all_issues.append({
                            "level": "WARNING",
                            "section": "narrative",
                            "kind": "narrative-count",
                            "message": "Only one narrative is present; most repos should provide at least one additional audience or cross-cutting reading path",
                        })
                    elif len(narratives) > 4:
                        all_issues.append({
                            "level": "WARNING",
                            "section": "narrative",
                            "kind": "narrative-count",
                            "message": f"{len(narratives)} narratives are present; usually keep a repo to 2-4 non-redundant narratives",
                        })
                    for narrative in narratives:
                        if not isinstance(narrative, dict):
                            all_issues.append({"level": "ERROR", "section": "narrative", "message": "narratives.yaml contains a non-object narrative entry"})
                            continue
                        nid = narrative.get("id", "")
                        if nid in ids:
                            all_issues.append({"level": "ERROR", "section": "narrative", "message": f"Duplicate narrative id '{nid}'"})
                        ids.add(nid)
                        all_issues.extend(validate_narrative(narrative, story_ids))
                        narrative_story_ids = {
                            (entry.get("id", "") if isinstance(entry, dict) else entry)
                            for entry in (narrative.get("stories", []) or [])
                        }
                        if child_story_ids and narrative_story_ids and narrative_story_ids.isdisjoint(child_story_ids):
                            all_issues.append({
                                "level": "WARNING",
                                "section": "narrative",
                                "kind": "narrative-selection",
                                "message": f"Narrative '{nid}' uses only root stories even though child stories exist. Prefer more specific child stories when they carry the real explanatory detail.",
                                "related_entities": [nid, *sorted(narrative_story_ids)],
                                "evidence_refs": story_seed_refs[:3],
                                "conflict_type": "evidence_vs_model" if story_seed_refs else None,
                            })
                    if "system-overview" not in ids:
                        all_issues.append({"level": "ERROR", "section": "narrative", "message": "system-overview narrative is required — default repo overview path covering the main top-level components"})

        if atlas and all_stories and isinstance(narratives, list):
            all_issues.extend(
                detect_cross_artifact_conflicts(
                    atlas,
                    all_stories,
                    narratives,
                    narrative_seeds_payload=narrative_seeds_payload,
                    control_hotspots_payload=control_hotspots_payload,
                    state_access_summary_payload=state_access_summary_payload,
                )
            )

    meta_path = analysis_dir / "meta.json"
    if meta_path.exists():
        try:
            meta = json.loads(meta_path.read_text())
            if isinstance(meta, dict):
                all_issues.extend(validate_meta(meta, analysis_dir))
            else:
                all_issues.append({"level": "ERROR", "section": "meta", "message": "meta.json must be a JSON object"})
        except json.JSONDecodeError as e:
            all_issues.append({"level": "ERROR", "section": "meta", "message": f"JSON parse error: {e}"})

    valid, final_status = finalize_validation_run(analysis_dir, run_log_path, all_issues)
    print_summary_and_exit(analysis_dir, use_lock, lock_path, all_issues, valid, final_status)


if __name__ == "__main__":
    main()
