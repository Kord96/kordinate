# log.json Schema

Defines the validator-owned lifecycle contract for one analysis run.

`log.json` is not a semantic output. It is a structured validator log. The current `log_type` is `validation`, and future log types may be added under the same neutral filename.

## Minimal Shape

```json
{
  "version": "1",
  "log_type": "validation",
  "analysis_dir": "<absolute path>",
  "latest_status": "valid | needs_refinement | invalid",
  "latest_iteration": 2,
  "updated_at": "<UTC timestamp>",
  "iterations": [
    {
      "iteration": 1,
      "timestamp": "<UTC timestamp>",
      "status": "valid | needs_refinement | invalid",
      "error_count": 0,
      "warning_count": 12,
      "summary": {
        "by_level": {
          "ERROR": 0,
          "WARNING": 12
        },
        "by_kind": {
          "grounding": 10,
          "story-decomposition": 2
        },
        "by_family": {
          "grounding": 10,
          "teaching-structure": 2
        }
      },
      "priority_summary": {
        "high": 0,
        "medium": 2,
        "low": 10
      },
      "conflict_summary": {
        "open_consistency_conflicts": 2,
        "by_conflict_type": {
          "cross_artifact": 1,
          "shape_tension": 1
        }
      },
      "repair_targets": [
        {
          "id": "grounding::story::reply-send-branching",
          "priority": "low",
          "family": "grounding",
          "kind": "grounding",
          "label": "reply-send-branching",
          "issue_count": 6,
          "sections": ["story"],
          "issue_ids": ["<stable short id>"],
          "messages": ["<representative issue message>"],
          "recommended_artifacts": ["observations/concepts.json"],
          "suggested_resolution": "<short repair hint>"
        }
      ],
      "quality_gate": {
        "passed": false,
        "failure_reasons": [
          "medium-priority issues remain",
          "warning count remains high after structural validity"
        ]
      },
      "issues": [
        {
          "id": "<stable short id>",
          "level": "ERROR | WARNING",
          "section": "<validator section>",
          "kind": "<normalized issue kind>",
          "family": "<broader repair family>",
          "priority": "high | medium | low",
          "is_consistency_conflict": false,
          "conflict_type": "cross_artifact | evidence_vs_model | shape_tension | null",
          "message": "<validator message>",
          "related_entities": [
            "<optional related story/component/narrative ids>"
          ],
          "evidence_refs": [
            "<optional file:line or other evidence ref>"
          ],
          "related_issue_ids": [
            "<optional linked issue ids>"
          ],
          "recommended_artifacts": [
            "<script-derived artifacts to consult first>"
          ],
          "status": "open | unchanged | regressed",
          "first_seen_iteration": 1,
          "last_seen_iteration": 1,
          "suggested_resolution": "<short repair hint>"
        }
      ],
      "resolved_issues": [
        {
          "id": "<stable short id>",
          "level": "ERROR | WARNING",
          "section": "<validator section>",
          "kind": "<normalized issue kind>",
          "family": "<broader repair family>",
          "priority": "high | medium | low",
          "is_consistency_conflict": false,
          "conflict_type": "cross_artifact | evidence_vs_model | shape_tension | null",
          "message": "<validator message>",
          "related_entities": [
            "<optional related story/component/narrative ids>"
          ],
          "evidence_refs": [
            "<optional file:line or other evidence ref>"
          ],
          "related_issue_ids": [
            "<optional linked issue ids>"
          ],
          "recommended_artifacts": [
            "<script-derived artifacts to consult first>"
          ],
          "status": "resolved",
          "first_seen_iteration": 1,
          "last_seen_iteration": 2,
          "resolution_summary": "<how the issue stopped appearing>",
          "suggested_resolution": "<short repair hint>"
        }
      ]
    }
  ]
}
```

## Rules

- the latest iteration is the authoritative current validation state
- `needs_refinement` means the run is structurally valid but has not cleared the post-validation quality gate
- repair loops should prioritize issues with status `open` or `regressed`
- repair loops should next prioritize `high` before `medium` before `low`
- issues marked `is_consistency_conflict: true` are contradiction-like problems that should be reconciled within the current run
- `conflict_type` distinguishes broad contradiction classes without requiring a separate contradiction artifact
- `related_entities` and `evidence_refs` help reconcile cross-artifact disagreements directly from the log
- `recommended_artifacts` points the repair loop at the highest-value script-derived artifacts for that issue or repair target
- `repair_targets` groups repeated low-level issues, especially grounding warnings, into claim-level repair buckets
- `quality_gate` records whether the run is clean enough to stop after structural validation
- a missing issue from the prior open set should move into `resolved_issues`
- issue ids are validator-owned and should be stable across repeated runs of the validator on the same unresolved finding
- this file is append-only across iterations within one run

### Recommended Repair Routing

Use the issue family and kind to decide which script-derived artifacts to consult first:

- grounding, naming
  - `facts/symbols-seed.json`
- state grounding, state truthfulness
  - `facts/state-seeds.json`
- health coverage, boundary health, propagation, containment
  - `observations/health.json`
  - `facts/state-access-summary.json`
  - `facts/control-hotspots.json`
- story-decomposition, narrative-selection, teaching-structure
  - `observations/stories.json`
  - `observations/components.json`
  - `observations/narratives.json`
  - `facts/control-hotspots.json`
  - `facts/state-access-summary.json`
- concepts, fact-vs-semantic, concept quality
  - `observations/concepts.json`
- root-shape, atlas-story tension, component-model
  - `observations/components.json`
  - `observations/stories.json`

Treat these artifacts as repair constraints and evidence, not as unquestioned truth.

## Purpose

Use `log.json` to:
- understand what is still broken
- see what has already been fixed
- distinguish provenance, grounding, teaching-structure, and cross-artifact-consistency problems
- identify contradiction-like issues without a separate artifact
- prioritize the next repair step
- compare repair convergence across iterations
