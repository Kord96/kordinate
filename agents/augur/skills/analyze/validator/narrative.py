"""Validate `narratives.yaml` and cross-artifact reading-path consistency.

Checks owned here:
- required narrative fields and canonical narrative ids
- story membership, teaching goals, throughline, and overview quality
- narrative/story coherence within one narrative
- overlap, omission, and selection conflicts across atlas, stories, and narratives

This module does not validate story YAML field shape or atlas structure; it
assumes those artifacts were already parsed by `main.py`.
"""

import re

from .constants import CANONICAL_NARRATIVE_IDS

def validate_narrative(narrative: dict, story_ids: set) -> list[dict]:
    issues = []

    def error(msg):
        issues.append({"level": "ERROR", "section": "narrative", "message": msg})

    def warn(msg):
        issues.append({"level": "WARNING", "section": "narrative", "message": msg})

    jid = narrative.get("id", "<unknown>")

    if "id" not in narrative:
        error("Narrative missing required field: id")
    if "title" not in narrative:
        error(f"Narrative '{jid}' missing required field: title")
    if "description" not in narrative:
        error(f"Narrative '{jid}' missing required field: description")
    if jid and jid not in CANONICAL_NARRATIVE_IDS:
        error(
            f"Narrative '{jid}' is outside the canonical narrative palette; use one of: "
            + ", ".join(sorted(CANONICAL_NARRATIVE_IDS))
        )

    stories = narrative.get("stories", [])
    teaches = narrative.get("teaches")
    throughline = str(narrative.get("throughline") or "").strip()
    description = str(narrative.get("description") or "").strip()
    sentence_count = len([part for part in re.split(r"(?<=[.!?])\s+", description) if part.strip()]) if description else 0
    if len(stories) < 3:
        warn(f"Narrative '{jid}' has {len(stories)} stories (minimum 3)")
    elif len(stories) > 8:
        warn(f"Narrative '{jid}' has {len(stories)} stories (maximum 8)")
    if description:
        if sentence_count < 2:
            issues.append({
                "level": "WARNING",
                "section": "narrative",
                "kind": "narrative-overview",
                "message": f"Narrative '{jid}' description is too thin; write a compact 2-4 sentence overview instead of a one-liner",
            })
        elif sentence_count > 5:
            issues.append({
                "level": "WARNING",
                "section": "narrative",
                "kind": "narrative-overview",
                "message": f"Narrative '{jid}' description is too long for the overview slot; keep it to roughly 2-4 sentences",
            })
    if teaches is None:
        issues.append({
            "level": "WARNING",
            "section": "narrative",
            "kind": "narrative-coherence",
            "message": f"Narrative '{jid}' is missing `teaches`; define 2-4 explicit learning goals for the sequence",
        })
    elif not isinstance(teaches, list):
        error(f"Narrative '{jid}' teaches must be a list when present")
    else:
        cleaned_goals = [goal for goal in teaches if isinstance(goal, str) and goal.strip()]
        if len(cleaned_goals) < 2:
            issues.append({
                "level": "WARNING",
                "section": "narrative",
                "kind": "narrative-coherence",
                "message": f"Narrative '{jid}' should define at least 2 teaching goals in `teaches`",
            })
        elif len(cleaned_goals) > 4:
            issues.append({
                "level": "WARNING",
                "section": "narrative",
                "kind": "narrative-coherence",
                "message": f"Narrative '{jid}' has too many teaching goals; keep `teaches` to roughly 2-4 items",
            })
    if not throughline:
        issues.append({
            "level": "WARNING",
            "section": "narrative",
            "kind": "narrative-coherence",
            "message": f"Narrative '{jid}' is missing `throughline`; explain why these stories belong together in this order",
        })
    else:
        throughline_sentences = len([part for part in re.split(r"(?<=[.!?])\s+", throughline) if part.strip()])
        if throughline_sentences > 3:
            issues.append({
                "level": "WARNING",
                "section": "narrative",
                "kind": "narrative-coherence",
                "message": f"Narrative '{jid}' throughline is too long; keep it to one short paragraph",
            })

    for entry in stories:
        if isinstance(entry, dict):
            sid = entry.get("id", "")
            if not entry.get("description"):
                error(f"Narrative '{jid}' story '{sid or '?'}' is missing description")
        else:
            sid = entry
        if sid not in story_ids:
            error(f"Narrative '{jid}' references unknown story '{sid}'")

    return issues

def detect_cross_artifact_conflicts(
    atlas: dict,
    all_stories: dict[str, dict],
    narratives: list[dict],
    narrative_seeds_payload: dict | None = None,
    control_hotspots_payload: dict | None = None,
    state_access_summary_payload: dict | None = None,
) -> list[dict]:
    issues: list[dict] = []
    components = {
        str(component.get("id")): component
        for component in (atlas.get("components") or [])
        if isinstance(component, dict) and component.get("id")
    }
    state_ids = {
        str(state.get("id"))
        for state in (atlas.get("state") or [])
        if isinstance(state, dict) and state.get("id")
    }
    depends_on = {
        cid: set(str(dep) for dep in (component.get("depends_on") or []) if dep)
        for cid, component in components.items()
    }
    child_story_ids_by_parent: dict[str, list[str]] = {}
    for sid, story in all_stories.items():
        parent = str(story.get("parent") or "")
        if parent:
            child_story_ids_by_parent.setdefault(parent, []).append(sid)

    def story_root(story_id: str) -> str:
        current = all_stories.get(story_id) or {}
        seen: set[str] = set()
        current_id = story_id
        while current.get("parent") and current_id not in seen:
            seen.add(current_id)
            current_id = str(current.get("parent") or "")
            current = all_stories.get(current_id) or {}
        return current_id or story_id

    def story_component_ids(story: dict) -> set[str]:
        ids: set[str] = set()
        for struct in story.get("structures") or []:
            for node in struct.get("nodes") or []:
                nid = str(node.get("id") or "") if isinstance(node, dict) else str(node or "")
                if nid in components:
                    ids.add(nid)
        for flow in story.get("flows") or []:
            for step in flow.get("steps") or []:
                if not isinstance(step, dict):
                    continue
                component = str(step.get("node") or step.get("component") or "")
                target = str(step.get("to") or "")
                if component in components:
                    ids.add(component)
                if target in components:
                    ids.add(target)
        for obs in story.get("observations") or []:
            if isinstance(obs, dict):
                component = str(obs.get("component") or "")
                if component in components:
                    ids.add(component)
        return ids

    def story_primary_mode(story_id: str) -> str:
        story = all_stories.get(story_id) or {}
        return str(story.get("primary_mode") or "").strip()

    root_to_story_ids: dict[str, list[str]] = {}
    for sid in all_stories:
        root_to_story_ids.setdefault(story_root(sid), []).append(sid)

    control_hotspots_by_component: dict[str, list[dict]] = {}
    if isinstance(control_hotspots_payload, dict):
        for fact in control_hotspots_payload.get("facts") or []:
            if not isinstance(fact, dict):
                continue
            raw = fact.get("raw_evidence") or {}
            component = str(raw.get("component") or "")
            if component:
                control_hotspots_by_component.setdefault(component, []).append(fact)

    state_access_by_component: dict[str, list[dict]] = {}
    if isinstance(state_access_summary_payload, dict):
        for fact in state_access_summary_payload.get("facts") or []:
            if not isinstance(fact, dict):
                continue
            raw = fact.get("raw_evidence") or {}
            for component in raw.get("components") or []:
                component = str(component or "")
                if component:
                    state_access_by_component.setdefault(component, []).append(fact)

    system_overview_seed = (
        (narrative_seeds_payload or {}).get("system_overview") or {}
        if isinstance(narrative_seeds_payload, dict)
        else {}
    )
    recommended_narrative_records = [
        item
        for item in ((narrative_seeds_payload or {}).get("recommended_narratives") or [])
        if isinstance(item, dict) and str(item.get("id") or "")
    ] if isinstance(narrative_seeds_payload, dict) else []
    recommended_narrative_ids = {
        str(item.get("id") or "")
        for item in recommended_narrative_records
    }
    recommended_narrative_by_id = {
        str(item.get("id") or ""): item
        for item in recommended_narrative_records
    }
    optional_recommended_ids = {
        narrative_id
        for narrative_id in recommended_narrative_ids
        if narrative_id and narrative_id != "system-overview"
    }
    optional_recommended_records = [
        item
        for item in recommended_narrative_records
        if str(item.get("id") or "") in optional_recommended_ids
    ]
    optional_recommended_records.sort(
        key=lambda item: (
            -int(item.get("score") or 0),
            int(item.get("priority_rank") or 999),
            str(item.get("id") or ""),
        )
    )
    optional_budget = (
        (narrative_seeds_payload or {}).get("optional_narrative_budget") or {}
        if isinstance(narrative_seeds_payload, dict)
        else {}
    )
    preferred_optional_target = int(optional_budget.get("target") or 0)
    preferred_roots = [
        item for item in (system_overview_seed.get("preferred_root_components") or [])
        if isinstance(item, dict)
    ]
    preferred_flow_hotspots = [
        item for item in (system_overview_seed.get("preferred_flow_hotspots") or [])
        if isinstance(item, dict)
    ]
    preferred_boundary_targets = [
        item for item in (system_overview_seed.get("preferred_state_or_boundary_targets") or [])
        if isinstance(item, dict)
    ]
    preferred_root_ids = [str(item.get("id") or "") for item in preferred_roots if item.get("id")]
    require_flow_story = bool(system_overview_seed.get("require_flow_story"))
    require_state_or_boundary_story = bool(system_overview_seed.get("require_state_or_boundary_story"))
    prefer_child_stories = bool(system_overview_seed.get("prefer_child_stories"))
    present_ids = {
        str(narrative.get("id") or "")
        for narrative in narratives
        if isinstance(narrative, dict)
    }

    def text_tokens(value: str) -> set[str]:
        return {
            token
            for token in re.findall(r"[a-z0-9]+", value.lower())
            if len(token) > 3 and token not in {"this", "that", "with", "from", "into", "through", "their", "about", "because", "where", "which", "story", "next", "then"}
        }

    for sid, story in all_stories.items():
        for structure in story.get("structures") or []:
            for edge in structure.get("edges") or []:
                if not isinstance(edge, dict):
                    continue
                edge_type = str(edge.get("type") or "").lower()
                if edge_type not in {"calls", "reads", "writes"}:
                    continue
                source = str(edge.get("from") or "")
                target = str(edge.get("to") or "")
                if source not in components or target not in components or source == target:
                    continue
                if target in depends_on.get(source, set()):
                    continue
                if source in depends_on.get(target, set()):
                    issues.append(
                        {
                            "level": "WARNING",
                            "section": "components",
                            "kind": "component-model",
                            "message": (
                                f"Story '{sid}' implies '{source}' -> '{target}' via a '{edge_type}' edge, "
                                f"but atlas depends_on points the opposite direction"
                            ),
                            "conflict_type": "cross_artifact",
                            "related_entities": [sid, source, target],
                            "evidence_refs": [],
                        }
                    )

    for narrative in narratives:
        if not isinstance(narrative, dict):
            continue
        nid = str(narrative.get("id") or "")
        description = str(narrative.get("description") or "").strip()
        teaches = narrative.get("teaches") if isinstance(narrative.get("teaches"), list) else []
        throughline = str(narrative.get("throughline") or "").strip()
        story_entries = narrative.get("stories") or []
        referenced_story_ids = []
        for entry in story_entries:
            if isinstance(entry, dict):
                story_id = str(entry.get("id") or "")
            else:
                story_id = str(entry or "")
            if story_id:
                referenced_story_ids.append(story_id)
        referenced_set = set(referenced_story_ids)
        recommended_record = recommended_narrative_by_id.get(nid)
        if nid != "system-overview" and nid in CANONICAL_NARRATIVE_IDS and recommended_record is None:
            issues.append(
                {
                    "level": "WARNING",
                    "section": "narrative",
                    "kind": "narrative-selection",
                    "message": f"Narrative '{nid}' is in the canonical palette but is not strongly justified by deterministic narrative seeds",
                    "conflict_type": "evidence_vs_model",
                    "related_entities": [nid, *referenced_story_ids[:3]],
                    "evidence_refs": [],
                }
            )
        if nid != "system-overview" and nid in CANONICAL_NARRATIVE_IDS and recommended_record is not None:
            present_optional_ids = {
                story_nid
                for story_nid in present_ids
                if story_nid and story_nid != "system-overview"
            }
            stronger_missing = [
                item
                for item in optional_recommended_records
                if str(item.get("id") or "") not in present_optional_ids
                and int(item.get("score") or 0) >= int(recommended_record.get("score") or 0) + 10
            ]
            if stronger_missing:
                stronger = stronger_missing[0]
                issues.append(
                    {
                        "level": "WARNING",
                        "section": "narrative",
                        "kind": "narrative-selection",
                        "message": (
                            f"Narrative '{nid}' is weaker than the stronger deterministic optional narrative "
                            f"'{str(stronger.get('id') or '')}', which is missing from the repo's selected teaching paths"
                        ),
                        "conflict_type": "evidence_vs_model",
                        "related_entities": [nid, str(stronger.get("id") or "")],
                        "evidence_refs": [],
                    }
                )
        missing_child_coverage: list[str] = []
        for story_id in referenced_story_ids:
            child_ids = child_story_ids_by_parent.get(story_id) or []
            if len(child_ids) < 2:
                continue
            if not any(child_id in referenced_set for child_id in child_ids):
                missing_child_coverage.append(story_id)
        if missing_child_coverage:
            issues.append(
                {
                    "level": "WARNING",
                    "section": "narrative",
                    "kind": "narrative-selection",
                    "message": (
                        f"Narrative '{nid}' uses root stories {', '.join(sorted(missing_child_coverage))} "
                        "without any of their more specific child stories"
                    ),
                    "conflict_type": "cross_artifact",
                    "related_entities": [nid, *sorted(missing_child_coverage)],
                    "evidence_refs": [],
                }
            )

        if teaches:
            story_teaching_text = [
                " ".join(
                    str(part)
                    for part in (
                        (all_stories.get(story_id) or {}).get("teaches"),
                        (all_stories.get(story_id) or {}).get("title"),
                        (all_stories.get(story_id) or {}).get("summary"),
                    )
                    if part
                )
                for story_id in referenced_story_ids
                if story_id in all_stories
            ]
            story_tokens = set().union(*(text_tokens(text) for text in story_teaching_text)) if story_teaching_text else set()
            uncovered_goals = []
            for goal in teaches:
                if not isinstance(goal, str) or not goal.strip():
                    continue
                goal_tokens = text_tokens(goal)
                if goal_tokens and len(goal_tokens & story_tokens) == 0:
                    uncovered_goals.append(goal)
            if uncovered_goals:
                issues.append(
                    {
                        "level": "WARNING",
                        "section": "narrative",
                        "kind": "narrative-coherence",
                        "message": f"Narrative '{nid}' includes teaching goals that are not clearly served by the selected stories: {', '.join(uncovered_goals[:2])}",
                        "conflict_type": "cross_artifact",
                        "related_entities": [nid, *referenced_story_ids],
                        "evidence_refs": [],
                    }
                )

        if throughline:
            throughline_tokens = text_tokens(throughline)
            story_focus_tokens = set()
            for story_id in referenced_story_ids:
                story = all_stories.get(story_id) or {}
                story_focus_tokens |= text_tokens(" ".join(str(part) for part in (story.get("teaches"), story.get("title")) if part))
            if throughline_tokens and story_focus_tokens and len(throughline_tokens & story_focus_tokens) == 0:
                issues.append(
                    {
                        "level": "WARNING",
                        "section": "narrative",
                        "kind": "narrative-coherence",
                        "message": f"Narrative '{nid}' throughline does not clearly connect to the selected stories",
                        "conflict_type": "cross_artifact",
                        "related_entities": [nid, *referenced_story_ids],
                        "evidence_refs": [],
                    }
                )

            story_without_goal_support = []
            goal_tokens = [text_tokens(goal) for goal in teaches if isinstance(goal, str) and goal.strip()]
            for story_id in referenced_story_ids:
                story = all_stories.get(story_id) or {}
                story_text = " ".join(
                    str(part)
                    for part in (story.get("teaches"), story.get("title"), story.get("summary"))
                    if part
                )
                story_tokens = text_tokens(story_text)
                if goal_tokens and story_tokens and not any(story_tokens & goal for goal in goal_tokens):
                    story_without_goal_support.append(story_id)
            if story_without_goal_support:
                issues.append(
                    {
                        "level": "WARNING",
                        "section": "narrative",
                        "kind": "narrative-coherence",
                        "message": f"Narrative '{nid}' includes stories that do not clearly support its teaching goals: {', '.join(story_without_goal_support[:2])}",
                        "conflict_type": "cross_artifact",
                        "related_entities": [nid, *story_without_goal_support],
                        "evidence_refs": [],
                    }
                )

        transition_failures = []
        for index, entry in enumerate(story_entries):
            if index == 0 or not isinstance(entry, dict):
                continue
            bridge_text = str(entry.get("description") or "").strip()
            current_story_id = str(entry.get("id") or "")
            previous_entry = story_entries[index - 1]
            previous_story_id = str(previous_entry.get("id") if isinstance(previous_entry, dict) else previous_entry or "")
            previous_story = all_stories.get(previous_story_id) or {}
            current_story = all_stories.get(current_story_id) or {}
            transition_tokens = text_tokens(bridge_text)
            previous_tokens = text_tokens(" ".join(str(part) for part in (previous_story.get("teaches"), previous_story.get("title")) if part))
            current_tokens = text_tokens(" ".join(str(part) for part in (current_story.get("teaches"), current_story.get("title")) if part))
            if bridge_text and transition_tokens and (transition_tokens & previous_tokens) and (transition_tokens & current_tokens):
                continue
            transition_failures.append(current_story_id or f"story-{index+1}")
        if transition_failures:
            issues.append(
                {
                    "level": "WARNING",
                    "section": "narrative",
                    "kind": "narrative-coherence",
                    "message": f"Narrative '{nid}' has weak adjacent-story transitions; bridge text does not clearly connect the sequence around: {', '.join(transition_failures[:2])}",
                    "conflict_type": "cross_artifact",
                    "related_entities": [nid, *transition_failures],
                    "evidence_refs": [],
                }
            )

        if nid == "system-overview" and description:
            top_level_components = [
                component
                for component in components.values()
                if not component.get("parent") and not component.get("belongs_to")
            ]
            sentence_count = len([part for part in re.split(r"(?<=[.!?])\s+", description) if part.strip()])
            if sentence_count < 3:
                issues.append(
                    {
                        "level": "WARNING",
                        "section": "narrative",
                        "kind": "narrative-overview",
                        "message": "system-overview description is too short to serve as the repo overview; use roughly 3-4 sentences",
                        "conflict_type": "cross_artifact",
                        "related_entities": [nid],
                        "evidence_refs": [],
                    }
                )
            lowered = description.lower()
            covered = 0
            for component in top_level_components:
                candidates = {
                    str(component.get("id") or "").lower(),
                    str(component.get("name") or "").lower(),
                }
                if any(candidate and candidate in lowered for candidate in candidates):
                    covered += 1
            expected_mentions = min(2, len(top_level_components))
            if expected_mentions and covered < expected_mentions:
                issues.append(
                    {
                        "level": "WARNING",
                        "section": "narrative",
                        "kind": "narrative-overview",
                        "message": "system-overview description does not name enough of the main top-level slices to function as a useful repo overview",
                        "conflict_type": "cross_artifact",
                        "related_entities": [nid, *[str(component.get('id')) for component in top_level_components]],
                        "evidence_refs": [],
                    }
                )
            teach_text = " ".join(
                [description, throughline]
                + [str(goal) for goal in teaches if isinstance(goal, str)]
            ).lower()
            what_tokens = {"purpose", "capability", "serves", "provides", "answers", "classifies", "stores", "scans", "emits", "manages", "handles"}
            how_tokens = {"flow", "pipeline", "path", "through", "runtime", "control", "orchestrates", "routes", "executes", "persists", "publishes"}
            if not any(token in teach_text for token in what_tokens):
                issues.append(
                    {
                        "level": "WARNING",
                        "section": "narrative",
                        "kind": "narrative-overview",
                        "message": "system-overview does not clearly answer what the system does; make the repo capability explicit in description or teaches",
                        "conflict_type": "cross_artifact",
                        "related_entities": [nid],
                        "evidence_refs": [],
                    }
                )
            if not any(token in teach_text for token in how_tokens):
                issues.append(
                    {
                        "level": "WARNING",
                        "section": "narrative",
                        "kind": "narrative-overview",
                        "message": "system-overview does not clearly answer how the system does it; make the operating model explicit in description, teaches, or throughline",
                        "conflict_type": "cross_artifact",
                        "related_entities": [nid],
                        "evidence_refs": [],
                    }
                )

        if nid == "system-overview":
            selected_roots = {story_root(story_id) for story_id in referenced_story_ids if story_id in all_stories}
            selected_modes = [story_primary_mode(story_id) for story_id in referenced_story_ids if story_id in all_stories]
            flow_count = sum(1 for mode in selected_modes if mode == "flow")
            structure_like_count = sum(1 for mode in selected_modes if mode in {"structure", "state", "decision"})
            available_structure_like = any(
                story_primary_mode(story_id) in {"structure", "state", "decision"}
                for story_id in all_stories
            )
            if (
                len(selected_modes) >= 4
                and flow_count >= max(3, len(selected_modes) - 1)
                and structure_like_count <= 1
                and available_structure_like
            ):
                issues.append(
                    {
                        "level": "WARNING",
                        "section": "narrative",
                        "kind": "narrative-selection",
                        "message": (
                            "system-overview leans too heavily on flow-first stories; include more structure- or state-first stories so the repo overview teaches system shape as well as motion"
                        ),
                        "conflict_type": "cross_artifact",
                        "related_entities": [nid, *referenced_story_ids],
                        "evidence_refs": [],
                    }
                )
            if preferred_root_ids:
                expected_root_count = min(2, len(preferred_root_ids))
                covered_preferred = [root_id for root_id in preferred_root_ids if root_id in selected_roots]
                if len(covered_preferred) < expected_root_count:
                    missing = [root_id for root_id in preferred_root_ids[:expected_root_count] if root_id not in covered_preferred]
                    evidence_refs = []
                    for item in preferred_roots[:expected_root_count]:
                        for ref in item.get("representative_files") or []:
                            ref = str(ref)
                            if ref and ref not in evidence_refs:
                                evidence_refs.append(ref)
                    issues.append(
                        {
                            "level": "WARNING",
                            "section": "narrative",
                            "kind": "narrative-selection",
                        "message": f"system-overview omits preferred repo-overview roots suggested by deterministic evidence: {', '.join(missing[:2])}",
                            "conflict_type": "evidence_vs_model",
                            "related_entities": [nid, *missing],
                            "evidence_refs": evidence_refs[:3],
                        }
                    )

            selected_stories = [all_stories.get(story_id) or {} for story_id in referenced_story_ids if story_id in all_stories]
            selected_component_ids = set().union(*(story_component_ids(story) for story in selected_stories)) if selected_stories else set()
            flow_story_ids = [
                story_id
                for story_id in referenced_story_ids
                if isinstance(all_stories.get(story_id), dict) and (all_stories.get(story_id) or {}).get("flows")
            ]
            if require_flow_story and not flow_story_ids:
                hotspot_refs: list[str] = []
                for root_id in selected_roots or preferred_root_ids:
                    for fact in control_hotspots_by_component.get(root_id, []):
                        for source in fact.get("source_files") or []:
                            source = str(source)
                            if source and source not in hotspot_refs:
                                hotspot_refs.append(source)
                issues.append(
                    {
                        "level": "WARNING",
                        "section": "narrative",
                        "kind": "narrative-selection",
                        "message": "system-overview does not include a clearly flow-bearing story even though deterministic signals suggest the repo overview should teach the operating model through a real flow",
                        "conflict_type": "evidence_vs_model",
                        "related_entities": [nid, *referenced_story_ids],
                        "evidence_refs": hotspot_refs[:3],
                    }
                )
            hotspot_components = {
                str(item.get("component") or "")
                for item in preferred_flow_hotspots
                if str(item.get("component") or "")
            }
            if hotspot_components and selected_component_ids and selected_component_ids.isdisjoint(hotspot_components):
                hotspot_refs: list[str] = []
                for item in preferred_flow_hotspots[:3]:
                    for ref in item.get("source_files") or []:
                        ref = str(ref)
                        if ref and ref not in hotspot_refs:
                            hotspot_refs.append(ref)
                issues.append(
                    {
                        "level": "WARNING",
                        "section": "narrative",
                        "kind": "narrative-selection",
                        "message": "system-overview avoids the strongest deterministic control hotspots, so the repo overview may miss the repo's defining operating path",
                        "conflict_type": "evidence_vs_model",
                        "related_entities": [nid, *sorted(hotspot_components)[:3]],
                        "evidence_refs": hotspot_refs[:3],
                    }
                )

            if require_state_or_boundary_story:
                has_state_or_boundary_story = False
                for story in selected_stories:
                    component_ids = story_component_ids(story)
                    if any(component in state_access_by_component for component in component_ids):
                        has_state_or_boundary_story = True
                        break
                    if any(str(step.get("to") or "") in state_ids for flow in story.get("flows") or [] for step in flow.get("steps") or [] if isinstance(step, dict)):
                        has_state_or_boundary_story = True
                        break
                if not has_state_or_boundary_story:
                    boundary_refs: list[str] = []
                    for root_id in selected_roots or preferred_root_ids:
                        for fact in state_access_by_component.get(root_id, []):
                            for source in fact.get("source_files") or []:
                                source = str(source)
                                if source and source not in boundary_refs:
                                    boundary_refs.append(source)
                    issues.append(
                        {
                            "level": "WARNING",
                            "section": "narrative",
                            "kind": "narrative-selection",
                        "message": "system-overview does not include a story that clearly teaches a state or dependency boundary even though deterministic evidence suggests one is central to the repo overview",
                            "conflict_type": "evidence_vs_model",
                            "related_entities": [nid, *referenced_story_ids],
                            "evidence_refs": boundary_refs[:3],
                        }
                    )
                boundary_components = {
                    component
                    for item in preferred_boundary_targets
                    for component in (item.get("components") or [])
                    if component
                }
                if boundary_components and selected_component_ids and selected_component_ids.isdisjoint(boundary_components):
                    boundary_refs: list[str] = []
                    for item in preferred_boundary_targets[:3]:
                        for ref in item.get("source_files") or []:
                            ref = str(ref)
                            if ref and ref not in boundary_refs:
                                boundary_refs.append(ref)
                    issues.append(
                        {
                            "level": "WARNING",
                            "section": "narrative",
                            "kind": "narrative-selection",
                        "message": "system-overview avoids the strongest deterministic state or boundary targets, so the repo overview may miss an important system boundary",
                            "conflict_type": "evidence_vs_model",
                            "related_entities": [nid, *sorted(boundary_components)[:3]],
                            "evidence_refs": boundary_refs[:3],
                        }
                    )

            if prefer_child_stories and referenced_story_ids:
                selected_child_story_ids = [story_id for story_id in referenced_story_ids if (all_stories.get(story_id) or {}).get("parent")]
                if not selected_child_story_ids and child_story_ids_by_parent:
                    issues.append(
                        {
                            "level": "WARNING",
                            "section": "narrative",
                            "kind": "narrative-selection",
                            "message": "system-overview stays root-only even though deterministic narrative seeds suggest a child story would teach the architecture more clearly",
                            "conflict_type": "evidence_vs_model",
                            "related_entities": [nid, *referenced_story_ids],
                            "evidence_refs": [],
                        }
                    )

    present_optional_recommended = sorted(optional_recommended_ids & present_ids)
    if preferred_optional_target > 0 and len(present_optional_recommended) < preferred_optional_target and optional_recommended_records:
        missing_ranked = [
            item
            for item in optional_recommended_records
            if str(item.get("id") or "") not in present_ids
        ]
        if missing_ranked:
            preferred_missing = [str(item.get("id") or "") for item in missing_ranked[:preferred_optional_target]]
            issues.append(
                {
                    "level": "WARNING",
                    "section": "narrative",
                    "kind": "narrative-selection",
                    "message": (
                        "Script-derived narrative seeds suggest the repo is missing one of its strongest optional "
                        f"teaching paths: {', '.join(preferred_missing)}"
                    ),
                    "conflict_type": "evidence_vs_model",
                    "related_entities": preferred_missing,
                    "evidence_refs": [],
                }
            )
    if optional_recommended_ids and not present_optional_recommended:
        record = optional_recommended_records[0] if optional_recommended_records else None
        exemplar_id = str((record or {}).get("id") or (sorted(optional_recommended_ids)[0] if optional_recommended_ids else ""))
        evidence_refs: list[str] = []
        evidence = (record or {}).get("evidence") or {}
        if isinstance(evidence, dict):
            for key in ("domains", "flow_hotspots", "targets", "concepts"):
                for value in evidence.get(key) or []:
                    if isinstance(value, str) and value and value not in evidence_refs:
                        evidence_refs.append(value)
        issues.append(
            {
                "level": "WARNING",
                "section": "narrative",
                "kind": "narrative-selection",
                "message": "Script-derived narrative seeds suggest the repo would benefit from at least one additional canonical narrative beyond system-overview, but none are present",
                "conflict_type": "evidence_vs_model",
                "related_entities": sorted(optional_recommended_ids),
                "evidence_refs": evidence_refs[:3],
            }
                    )

    valid_narratives = [
        narrative for narrative in narratives
        if isinstance(narrative, dict) and str(narrative.get("id") or "")
    ]
    narrative_story_sets: dict[str, set[str]] = {}
    narrative_text_tokens: dict[str, set[str]] = {}
    narrative_goal_tokens: dict[str, set[str]] = {}
    for narrative in valid_narratives:
        nid = str(narrative.get("id") or "")
        story_entries = narrative.get("stories") or []
        story_ids_for_narrative: list[str] = []
        for entry in story_entries:
            if isinstance(entry, dict):
                sid = str(entry.get("id") or "")
            else:
                sid = str(entry or "")
            if sid:
                story_ids_for_narrative.append(sid)
        narrative_story_sets[nid] = set(story_ids_for_narrative)
        description = str(narrative.get("description") or "")
        throughline = str(narrative.get("throughline") or "")
        teaches = narrative.get("teaches") if isinstance(narrative.get("teaches"), list) else []
        narrative_text_tokens[nid] = text_tokens(" ".join([description, throughline, *[str(goal) for goal in teaches if isinstance(goal, str)]]))
        narrative_goal_tokens[nid] = set().union(*(text_tokens(str(goal)) for goal in teaches if isinstance(goal, str) and goal.strip())) if teaches else set()

    checked_pairs: set[tuple[str, str]] = set()
    for left in valid_narratives:
        left_id = str(left.get("id") or "")
        left_set = narrative_story_sets.get(left_id) or set()
        if not left_id or not left_set:
            continue
        for right in valid_narratives:
            right_id = str(right.get("id") or "")
            right_set = narrative_story_sets.get(right_id) or set()
            if not right_id or not right_set or left_id == right_id:
                continue
            pair = tuple(sorted((left_id, right_id)))
            if pair in checked_pairs:
                continue
            checked_pairs.add(pair)
            intersection = left_set & right_set
            union = left_set | right_set
            if not union:
                continue
            jaccard = len(intersection) / len(union)
            symmetric_difference = len(union - intersection)
            left_text = narrative_text_tokens.get(left_id) or set()
            right_text = narrative_text_tokens.get(right_id) or set()
            left_goals = narrative_goal_tokens.get(left_id) or set()
            right_goals = narrative_goal_tokens.get(right_id) or set()
            text_overlap = (len(left_text & right_text) / len(left_text | right_text)) if (left_text or right_text) else 0.0
            goal_overlap = (len(left_goals & right_goals) / len(left_goals | right_goals)) if (left_goals or right_goals) else 0.0

            if jaccard >= 0.75 and symmetric_difference <= 2:
                issues.append(
                    {
                        "level": "WARNING",
                        "section": "narrative",
                        "kind": "narrative-selection",
                        "message": (
                            f"Narratives '{left_id}' and '{right_id}' reuse almost the same story set; "
                            "merge them or make their teaching paths more distinct"
                        ),
                        "conflict_type": "cross_artifact",
                        "related_entities": [left_id, right_id, *sorted(intersection)[:3]],
                        "evidence_refs": [],
                    }
                )
                continue

            if jaccard >= 0.6 and text_overlap >= 0.55 and goal_overlap >= 0.45:
                issues.append(
                    {
                        "level": "WARNING",
                        "section": "narrative",
                        "kind": "narrative-coherence",
                        "message": (
                            f"Narratives '{left_id}' and '{right_id}' have highly overlapping stories and teaching text; "
                            "differentiate their goals or replace the weaker narrative"
                        ),
                        "conflict_type": "cross_artifact",
                        "related_entities": [left_id, right_id, *sorted(intersection)[:3]],
                        "evidence_refs": [],
                    }
                )

    return issues
