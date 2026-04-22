# Concepts Facts Schema

Stable contract for run-local `facts/concepts.json`.

`concepts.json` is a specialized facts artifact. It is not a final concept list. It is a deterministic concepts package used to resolve whether a concept should be accepted, kept tentative, or rejected during the semantic phase.

## Interpretation Rules

- Treat each entry as a candidate concept, not a final architectural judgment.
- Use supporting evidence, counter evidence, evidence gaps, and review questions together.
- Prefer direct repo evidence when it contradicts or weakens the deterministic candidate.
- Do not accept a concept confidently when its required review questions remain materially unanswered.

## Minimal Shape

```json
{
  "version": "1",
  "generated": "<YYYY-MM-DD>",
  "project": "<project-name>",
  "analysis_mode": "full | incremental | design",
  "candidates": [
    {
      "id": "<stable candidate id>",
      "concept": "<canonical concept slug>",
      "summary": "<one sentence describing why this concept was suggested>",
      "status_hint": "candidate | strong-candidate | weak-candidate",
      "confidence": "high | medium | low",
      "supporting_evidence": [
        {
          "kind": "fact | file | symbol | detector",
          "ref": "<fact id or path:line or detector id>",
          "summary": "<short supporting point>"
        }
      ],
      "counter_evidence": [
        {
          "kind": "fact | file | symbol | detector",
          "ref": "<fact id or path:line or detector id>",
          "summary": "<short counter point>"
        }
      ],
      "evidence_gaps": [
        "<missing guardrail or expected support>"
      ],
      "review_questions": [
        {
          "id": "<stable question id>",
          "prompt": "<question text>",
          "weight": 3,
          "signals": ["<signal>"]
        }
      ],
      "recommended_next_step": "answer_questions | inspect_code | reject_if_unsupported | none",
      "related_files": ["<repo-relative-or-run-relative path>"],
      "related_fact_ids": ["<fact-id>"]
    }
  ]
}
```

## Required Candidate Fields

Each candidate concept entry must include:
- `id`
- `concept`
- `summary`
- `supporting_evidence`
- `counter_evidence`
- `evidence_gaps`
- `review_questions`
- `recommended_next_step`

`status_hint`, `confidence`, `related_files`, and `related_fact_ids` are optional but recommended.

## Semantic-Phase Expectations

The semantic phase should resolve each materially relevant candidate as:
- `accepted`
- `tentative`
- `rejected`

`concepts.json` itself should not be rewritten into those final labels. The final resolved concept view belongs in `atlas.json`.
