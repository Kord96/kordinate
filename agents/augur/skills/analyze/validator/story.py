"""Validate one story YAML artifact.

Checks owned here:
- required story fields and primary mode
- anchor object, anchor grounding, and evidence overlap
- story structures, flows, rationale, and teaching/thesis quality
- references from a story to atlas nodes and entities
- mode-specific expectations for structure/flow/state/failure/decision stories

This module validates one story at a time. It does not validate the story tree
across files; `main.py` handles cross-story counting and parent/child checks.
"""

import re
from pathlib import Path

from .helpers import (
    check_grounded_in,
    validate_evidence_file,
    verify_grounding_quality,
)

def validate_story(
    story: dict,
    atlas_node_ids: set,
    atlas_entity_ids: set,
    grounded_symbol_names: set[str] | None = None,
    atlas_story_node_details: dict[str, dict] | None = None,
    project_root: Path | None = None,
    analysis_dir: Path | None = None,
) -> list[dict]:
    issues = []
    atlas_story_node_details = atlas_story_node_details or {}
    grounded_symbol_names = grounded_symbol_names or set()
    warned_story_node_detail_ids: set[str] = set()
    allowed_primary_modes = {"structure", "flow", "state", "failure", "decision"}

    def error(msg):
        issues.append({"level": "ERROR", "section": "story", "message": msg})

    def warn(msg):
        issues.append({"level": "WARNING", "section": "story", "message": msg})

    def warn_story_node_detail(nid: str):
        if nid in warned_story_node_detail_ids:
            return
        warned_story_node_detail_ids.add(nid)
        detail = atlas_story_node_details.get(nid) or {}
        if not detail:
            return
        description = str(detail.get("description") or "").strip()
        summary = str(detail.get("summary") or "").strip()
        kind = str(detail.get("kind") or "atlas node")
        if not description:
            issues.append({
                "level": "WARNING",
                "section": "story",
                "kind": "story-quality",
                "message": f"Story '{sid}' uses {kind} '{nid}' but it has no description; story-used atlas nodes need basic drilldown prose",
                "related_entities": [sid, nid],
            })
        if not summary:
            issues.append({
                "level": "WARNING",
                "section": "story",
                "kind": "story-quality",
                "message": f"Story '{sid}' uses {kind} '{nid}' but it has no summary; story-used atlas nodes need richer drilldown prose for the drawer",
                "related_entities": [sid, nid],
            })
        elif len(summary.split()) < 12:
            issues.append({
                "level": "WARNING",
                "section": "story",
                "kind": "story-quality",
                "message": f"Story '{sid}' uses {kind} '{nid}' but its summary is too thin for drilldown; explain ownership, dependency shape, and why it matters",
                "related_entities": [sid, nid],
            })

    sid = story.get("id", "<unknown>")
    parent_story = story.get("parent")

    if "id" not in story:
        error(f"Story missing required field: id")
    if "title" not in story:
        error(f"Story '{sid}' missing required field: title")
    if "teaches" not in story:
        error(f"Story '{sid}' missing required field: teaches")
    if "primary_mode" not in story:
        error(f"Story '{sid}' missing required field: primary_mode")
    if "summary" not in story:
        error(f"Story '{sid}' missing required field: summary")

    primary_mode = str(story.get("primary_mode") or "").strip()
    if primary_mode and primary_mode not in allowed_primary_modes:
        error(
            f"Story '{sid}' primary_mode '{primary_mode}' is invalid; use one of: "
            + ", ".join(sorted(allowed_primary_modes))
        )

    teaches_text = str(story.get("teaches") or "").strip()
    if teaches_text:
        if len(teaches_text.split()) < 5:
            warn(f"Story '{sid}' teaches is too thin; make it a real thesis sentence")
        if len(re.findall(r"[.!?]", teaches_text)) > 1:
            warn(f"Story '{sid}' teaches should usually stay to one sentence")
    else:
        warn(f"Story '{sid}' teaches is empty; make the main lesson explicit")

    anchor = story.get("anchor")
    if not isinstance(anchor, dict):
        error(f"Story '{sid}' missing required object field: anchor")
    else:
        anchor_file = anchor.get("file")
        anchor_line = anchor.get("line")
        anchor_description = anchor.get("description")
        if not anchor_file:
            error(f"Story '{sid}' anchor is missing file")
        elif project_root or analysis_dir:
            issues.extend(check_grounded_in([f"{anchor_file}:{anchor_line or 1}"], project_root, analysis_dir, "story", f"{sid}/anchor"))
            issues.extend(verify_grounding_quality(
                [f"{anchor_file}:{anchor_line or 1}"],
                " ".join(str(part) for part in (anchor_description, story.get("title"), story.get("summary")) if part),
                project_root,
                analysis_dir,
                "story",
                f"{sid}/anchor",
            ))
        if not isinstance(anchor_line, int):
            error(f"Story '{sid}' anchor line must be an integer")
        if not anchor_description:
            error(f"Story '{sid}' anchor is missing description")

    # Summary word count
    summary = story.get("summary", "")
    word_count = len(summary.split())
    if word_count > 100:
        warn(f"Story '{sid}' summary is {word_count} words (max 100)")
    if word_count < 18:
        warn(f"Story '{sid}' summary is thin; use it to explain the concern, not just relabel it")

    structures = story.get("structures", []) or []
    flows = story.get("flows", []) or []
    observations = story.get("observations", []) or []
    rationale_entries = story.get("rationale", []) or []
    if not (structures or flows or observations or rationale_entries):
        error(f"Story '{sid}' has no primary explainer or support content")

    # Bold refs in visible story prose should resolve to atlas entities or grounded symbols.
    prose_fields = [summary, teaches_text]
    prose_fields.extend(str(obs.get("finding") or "") for obs in observations if isinstance(obs, dict))
    prose_fields.extend(
        " ".join(
            str(part or "")
            for part in (
                entry.get("decision"),
                entry.get("context"),
                entry.get("trade_offs"),
            )
        ).strip()
        for entry in rationale_entries if isinstance(entry, dict)
    )
    bold_refs = []
    for field in prose_fields:
        if field:
            bold_refs.extend(re.findall(r"\*\*([^*]+)\*\*", field))
    for ref in bold_refs:
        ref_text = str(ref).strip()
        ref_kebab = ref_text.lower().replace(" ", "-")
        if ref_kebab in atlas_entity_ids or ref_text in atlas_entity_ids:
            continue
        if ref_text in grounded_symbol_names:
            continue
        error(f"Story '{sid}' bold ref '**{ref_text}**' doesn't match any atlas entity or grounded symbol")

    # Structure node refs
    for struct in structures:
        struct_id = str(struct.get("id") or "?")
        struct_summary = str(struct.get("summary") or "").strip()
        struct_focus = str(struct.get("focus") or "").strip()
        if not struct_summary:
            issues.append({
                "level": "WARNING",
                "section": "story",
                "kind": "story-quality",
                "message": f"Story '{sid}' structure '{struct_id}' is missing summary; each visible graph should explain what slice it is showing",
                "related_entities": [sid, struct_id],
            })
        elif len(struct_summary.split()) < 5:
            issues.append({
                "level": "WARNING",
                "section": "story",
                "kind": "story-quality",
                "message": f"Story '{sid}' structure '{struct_id}' has a thin summary; explain the graph more clearly",
                "related_entities": [sid, struct_id],
            })
        if not struct_focus:
            issues.append({
                "level": "WARNING",
                "section": "story",
                "kind": "story-quality",
                "message": f"Story '{sid}' structure '{struct_id}' is missing focus; say what the reader should notice first in the graph",
                "related_entities": [sid, struct_id],
            })
        elif len(struct_focus.split()) < 4:
            issues.append({
                "level": "WARNING",
                "section": "story",
                "kind": "story-quality",
                "message": f"Story '{sid}' structure '{struct_id}' has a thin focus; make the main takeaway more explicit",
                "related_entities": [sid, struct_id],
            })
        structure_edges = struct.get("edges", []) or []
        referenced_by_edge = set()
        for edge in structure_edges:
            if isinstance(edge, dict):
                if edge.get("from"):
                    referenced_by_edge.add(edge.get("from"))
                if edge.get("to"):
                    referenced_by_edge.add(edge.get("to"))
        for node in struct.get("nodes", []):
            nid = node.get("id", "") if isinstance(node, dict) else node
            if nid and nid not in atlas_node_ids:
                error(f"Story '{sid}' structure node '{nid}' not in atlas")
            elif nid:
                warn_story_node_detail(nid)
            if isinstance(node, dict):
                observation_ids = [obs_id for obs_id in (node.get("observation_ids") or []) if obs_id]
                child_ids = [child_id for child_id in (node.get("children") or []) if child_id]
                if child_ids and not observation_ids:
                    issues.append({
                        "level": "WARNING",
                        "section": "story",
                        "kind": "story-quality",
                        "message": f"Story '{sid}' structure node '{nid}' groups children but has no observation_ids grounding that grouping",
                        "related_entities": [sid, nid, *child_ids[:2]],
                    })
                if not child_ids and not observation_ids and nid not in referenced_by_edge:
                    issues.append({
                        "level": "WARNING",
                        "section": "story",
                        "kind": "story-quality",
                        "message": f"Story '{sid}' structure node '{nid}' is weakly grounded; add observation_ids or connect it through explicit structure edges",
                        "related_entities": [sid, nid],
                    })
        for edge in struct.get("edges", []):
            for key in ("from", "to"):
                ref = edge.get(key, "")
                if ref and ref not in atlas_node_ids:
                    error(f"Story '{sid}' structure edge {key} '{ref}' not in atlas")

    # Flow node refs
    flow_titles_or_summaries: list[str] = []
    for flow in flows:
        flow_summary = str(flow.get("summary") or "").strip()
        flow_title = str(flow.get("title") or "").strip()
        flow_trigger = str(flow.get("trigger") or "").strip()
        flow_outcome = str(flow.get("outcome") or "").strip()
        if flow_title:
            flow_titles_or_summaries.append(flow_title)
        if flow_summary:
            flow_titles_or_summaries.append(flow_summary)
        if not flow_trigger:
            issues.append({
                "level": "WARNING",
                "section": "story",
                "kind": "story-quality",
                "message": f"Story '{sid}' flow '{flow.get('id', '?')}' is missing trigger; make what starts the flow explicit",
                "related_entities": [sid, str(flow.get("id") or "?")],
            })
        if not flow_outcome:
            issues.append({
                "level": "WARNING",
                "section": "story",
                "kind": "story-quality",
                "message": f"Story '{sid}' flow '{flow.get('id', '?')}' is missing outcome; make what successful completion produces explicit instead of relying on the final step alone",
                "related_entities": [sid, str(flow.get("id") or "?")],
            })
        elif len(flow_outcome.split()) < 4:
            issues.append({
                "level": "WARNING",
                "section": "story",
                "kind": "story-quality",
                "message": f"Story '{sid}' flow '{flow.get('id', '?')}' has a thin outcome; describe the result of the flow more clearly",
                "related_entities": [sid, str(flow.get("id") or "?")],
            })
        if primary_mode == "flow":
            if not flow_summary:
                issues.append({
                    "level": "WARNING",
                    "section": "story",
                    "kind": "story-quality",
                    "message": f"Flow-first story '{sid}' should give each primary flow a short summary explaining why it matters",
                    "related_entities": [sid, str(flow.get("id") or "?")],
                })
            elif len(flow_summary.split()) < 6:
                issues.append({
                    "level": "WARNING",
                    "section": "story",
                    "kind": "story-quality",
                    "message": f"Flow-first story '{sid}' flow '{flow.get('id', '?')}' has a thin summary; explain trigger, outcome, or architectural significance",
                    "related_entities": [sid, str(flow.get("id") or "?")],
                })
        if "path" in flow_title.lower() or "path" in flow_summary.lower():
            issues.append({
                "level": "WARNING",
                "section": "story",
                "kind": "story-quality",
                "message": f"Story '{sid}' flow '{flow.get('id', '?')}' uses 'path' wording; prefer 'flow' consistently in the story contract",
                "related_entities": [sid, str(flow.get("id") or "?")],
            })
        for step in flow.get("steps", []):
            for key in ("node", "to"):
                ref = step.get(key, "")
                if ref and ref not in atlas_node_ids:
                    error(f"Story '{sid}' flow step {key} '{ref}' not in atlas")
                elif ref:
                    warn_story_node_detail(ref)

    # Observation grounded_in
    for obs in observations:
        oid = obs.get("id", "?")
        finding = obs.get("finding", "")
        if not obs.get("grounded_in"):
            warn(f"Story '{sid}' observation '{oid}' has no grounded_in")
        elif project_root or analysis_dir:
            issues.extend(check_grounded_in(obs["grounded_in"], project_root, analysis_dir, "story", f"{sid}/{oid}"))
            issues.extend(verify_grounding_quality(obs["grounded_in"], finding, project_root, analysis_dir, "story", f"{sid}/{oid}"))
        evidence = obs.get("evidence") if isinstance(obs.get("evidence"), dict) else None
        if evidence and (project_root or analysis_dir):
            issues.extend(validate_evidence_file(
                evidence.get("file"),
                evidence.get("lines"),
                finding,
                project_root,
                analysis_dir,
                "story",
                f"{sid}/{oid}/evidence",
            ))
        comp = obs.get("component", "")
        if comp and comp not in atlas_node_ids:
            error(f"Story '{sid}' observation component '{comp}' not in atlas")

    if len(observations) > 4:
        issues.append({
            "level": "WARNING",
            "section": "story",
            "kind": "story-quality",
            "message": f"Story '{sid}' has many observations ({len(observations)}); keep the visible story focused and push extra evidence into support material only when it changes understanding",
            "related_entities": [sid],
        })
    if len(rationale_entries) > 3:
        issues.append({
            "level": "WARNING",
            "section": "story",
            "kind": "story-quality",
            "message": f"Story '{sid}' has many rationale entries ({len(rationale_entries)}); keep decisions selective unless the story is decision-first",
            "related_entities": [sid],
        })

    mixed_primary_explainers = bool(structures) and bool(flows)
    if mixed_primary_explainers:
        if primary_mode in {"structure", "flow"}:
            issues.append({
                "level": "WARNING",
                "section": "story",
                "kind": "story-quality",
                "message": (
                    f"Story '{sid}' mixes structure and flow explainers even though it is {primary_mode}-first; "
                    "split the concern or demote one explainer unless both are truly necessary"
                ),
                "related_entities": [sid],
            })
        elif primary_mode == "decision" and (structures or flows):
            issues.append({
                "level": "WARNING",
                "section": "story",
                "kind": "story-quality",
                "message": (
                    f"Decision-first story '{sid}' includes both structure and flow explainers; "
                    "keep those only when they materially clarify the decision"
                ),
                "related_entities": [sid],
            })
        elif primary_mode in {"state", "failure"} and len(structures) > 1 and len(flows) > 1:
            issues.append({
                "level": "WARNING",
                "section": "story",
                "kind": "story-quality",
                "message": (
                    f"{primary_mode.title()}-first story '{sid}' mixes multiple structures and multiple flows; "
                    "keep one primary explainer and at most one supporting counterpart unless the concern is truly irreducible"
                ),
                "related_entities": [sid],
            })
    if primary_mode == "structure" and len(flows) > 1:
        issues.append({
            "level": "WARNING",
            "section": "story",
            "kind": "story-quality",
            "message": f"Structure-first story '{sid}' has too many supporting flows; keep at most one if the story really needs it",
            "related_entities": [sid],
        })
    if primary_mode == "flow" and len(structures) > 1:
        issues.append({
            "level": "WARNING",
            "section": "story",
            "kind": "story-quality",
            "message": f"Flow-first story '{sid}' has too many supporting structures; keep at most one if the story really needs it",
            "related_entities": [sid],
        })

    thesis_text = " ".join(part for part in (teaches_text, str(story.get("title") or ""), summary) if part).lower()
    state_tokens = ("state", "storage", "persist", "cache", "queue", "snapshot", "config", "session")
    failure_tokens = ("fail", "degrad", "stale", "lag", "retry", "outage", "incident", "recovery", "mitigat", "cascade")
    decision_tokens = ("trade-off", "tradeoff", "decision", "choose", "constraint", "because", "alternative")
    has_failure_support = any(token in thesis_text for token in failure_tokens) or any(
        any(
            token in " ".join(
                str(part) for part in (entry.get("decision"), entry.get("context"), entry.get("trade_offs")) if part
            ).lower()
            for token in failure_tokens
        )
        for entry in rationale_entries if isinstance(entry, dict)
    ) or any(
        any(
            token in " ".join(str(part) for part in (obs.get("finding"), obs.get("recommendation")) if part).lower()
            for token in failure_tokens
        )
        for obs in observations if isinstance(obs, dict)
    )

    if primary_mode == "structure":
        if not structures:
            error(f"Structure-first story '{sid}' is missing structures")
        if len(structures) > 2:
            warn(f"Structure-first story '{sid}' has too many structure views; keep one primary explainer and at most one supporting variant")
        if flows and len(flows) > len(structures):
            warn(f"Structure-first story '{sid}' includes more flows than structures; keep the structural explainer dominant")
    elif primary_mode == "flow":
        if not flows:
            error(f"Flow-first story '{sid}' is missing flows")
        if len(flows) > 2:
            warn(f"Flow-first story '{sid}' has too many flows; keep one primary flow and at most one supporting flow")
        if structures and len(structures) > len(flows):
            warn(f"Flow-first story '{sid}' includes more structure views than flows; keep the flow explainer dominant")
    elif primary_mode == "state":
        if not (structures or flows):
            error(f"State-first story '{sid}' should include a structure or flow that explains the state boundary")
        if not any(token in thesis_text for token in state_tokens):
            warn(f"State-first story '{sid}' thesis and summary do not clearly read as state-focused")
    elif primary_mode == "failure":
        if not (flows or observations):
            error(f"Failure-first story '{sid}' should include a flow or observation set that explains the failure mode")
        if not has_failure_support:
            warn(f"Failure-first story '{sid}' does not clearly describe degraded behavior, failure, or recovery")
    elif primary_mode == "decision":
        if not rationale_entries:
            error(f"Decision-first story '{sid}' is missing rationale")
        if not any(token in thesis_text for token in decision_tokens):
            warn(f"Decision-first story '{sid}' thesis and summary do not clearly frame the design choice or trade-off")
        if structures and flows and len(rationale_entries) < 1:
            warn(f"Decision-first story '{sid}' is leaning on structure and flow explainers without enough explicit rationale")

    if parent_story:
        child_nodes: set[str] = set()
        for struct in structures:
            for node in struct.get("nodes", []):
                if isinstance(node, dict):
                    nid = str(node.get("id") or "")
                else:
                    nid = str(node or "")
                if nid:
                    child_nodes.add(nid)
        if len(child_nodes) >= max(4, len(atlas_node_ids) // 3):
            warn(f"Story '{sid}' may be too broad for a child story; narrow the node set relative to its parent")

    return issues
