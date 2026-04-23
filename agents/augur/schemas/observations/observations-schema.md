# Observations Schema

Stable contract for run-local `observations/` artifacts produced between
deterministic facts and final semantic outputs.

Observations are normalized analytical assessments derived from deterministic
facts plus semantic signatures, review questions, and optionally direct repo
inspection. They are not facts, and they are not final semantic outputs.

## Purpose

Use `observations/` for normalized semantic working artifacts that may include:
- confidence
- counter-evidence
- gaps
- open questions
- recommendations

Do not use `observations/` for:
- detector output
- normalized fact records
- final atlas/story/narrative publication

## Output Layout

```text
<RUN>/
  facts/
    <domain>.json
  observations/
    <artifact>.json
  atlas.json
  stories/
  narratives.yaml
```

Observation files are optional. A run may produce none, one, or several
observation artifacts.

## Observation File Shape

```json
{
  "version": "1",
  "generated": "<RFC3339>",
  "project": "<project-name>",
  "analysis_mode": "full | incremental | design",
  "artifact": "<artifact-name>",
  "count": 0,
  "observations": []
}
```

## Observation Record Shape

```json
{
  "id": "<stable observation id>",
  "kind": "architecture | concept | flow | state | dependency | health | failure | story | narrative | repair",
  "subject": "<what this observation is about>",
  "status": "candidate | supported | contradicted | needs-review | resolved",
  "finding": "<analytical statement>",
  "confidence": "high | medium | low",
  "evidence": {
    "fact_ids": ["<fact id>"],
    "repo_refs": ["<path:line>"],
    "output_refs": ["<atlas component id or story id>"],
    "doc_refs": ["<concept or framework doc path>"]
  },
  "counter_evidence": ["<what weakens the observation>"],
  "gaps": ["<what remains unclear>"],
  "questions": [
    {
      "id": "<stable question id>",
      "prompt": "<follow-up semantic question>",
      "weight": 1,
      "signals": []
    }
  ],
  "recommendation": "<suggested next semantic step>",
  "next_actions": ["<concrete repo exploration step>"],
  "relationships": [
    {
      "type": "observation_ref",
      "label": "related_to | derived_from | supersedes",
      "target_id": "<observation id>"
    },
    {
      "type": "fact_ref",
      "label": "grounded_in",
      "target_id": "<fact id>"
    },
    {
      "type": "doc_ref",
      "label": "relevant_concept | relevant_framework",
      "target_path": "<doc path>"
    }
  ]
}
```

## Boundary With Facts

Facts:
- deterministic
- detector-produced
- no confidence
- no semantic recommendations

Observations:
- semantic assessment
- may be produced deterministically before the semantic phase
- confidence allowed
- questions and recommendations allowed

## Boundary With Final Outputs

Observations are not a substitute for:
- `atlas.json`
- `stories/*.yaml`
- `narratives.yaml`

They are intermediate semantic artifacts that can support:
- debugging
- validation
- repair
- repo exploration
- future semantic refinement
