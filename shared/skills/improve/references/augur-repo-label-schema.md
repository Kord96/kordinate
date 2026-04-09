# Augur Repo Label Schema

Defines the compact per-repo label file used for benchmark scoring.

The label file is intentionally partial. It should capture only the highest-value architecture facts needed for reliable evaluation.

## Recommended Path

```text
benchmark/labels/<owner>--<repo>.json
```

## Schema

```json
{
  "repo": "owner/name",
  "pinned_sha": "abc1234",
  "critical_components": [
    {
      "name": "extension-host",
      "aliases": ["plugin host"],
      "kind": "runtime-core",
      "required": true
    }
  ],
  "expected_concepts": [
    {
      "name": "plugin",
      "required": true,
      "confidence": "high"
    }
  ],
  "expected_anti_patterns": [
    {
      "name": "architecture-drift",
      "required": false,
      "confidence": "medium"
    }
  ],
  "expected_route_families": [
    {
      "name": "extension-management",
      "required": false
    }
  ],
  "expected_external_dependencies": [
    {
      "name": "filesystem",
      "required": true
    }
  ],
  "expected_state_stores": [
    {
      "name": "workspace-state",
      "required": false
    }
  ],
  "expected_failure_modes": [
    {
      "name": "plugin-load-failure",
      "required": true
    }
  ],
  "grounding_checks": [
    {
      "claim": "The repo has a distinct plugin or extension host boundary.",
      "evidence_hint": "Look for extension registration or host runtime code."
    }
  ],
  "notes_on_ambiguity": [
    "Some components may be split differently by different analyzers but still be acceptable."
  ]
}
```

## Labeling Rules

- Prefer `required: true` only for high-confidence critical items.
- Use aliases for naming variants the analyzer might reasonably produce.
- Keep labels architecture-focused, not exhaustive.
- Exclude ambiguous items from numeric scoring when needed.
- Grounding checks should be short, concrete, and evidence-oriented.

## Minimum Viable Label

At minimum, every repo label should include:

- `repo`
- `pinned_sha`
- `critical_components`
- `expected_concepts`
- `expected_external_dependencies`
- `expected_failure_modes`
- `grounding_checks`

Everything else is optional but recommended.
