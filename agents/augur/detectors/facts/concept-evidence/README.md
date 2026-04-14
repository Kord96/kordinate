# Concept-evidence detectors

Deterministic source assets for concept-evidence inference live here.

This layer is separate from semantic memory:
- `memory/catalog/concepts/` describes what a concept means
- `detectors/facts/concept-evidence/` describes how to infer concept-evidence facts
  deterministically

Suggested per-concept files:

```text
detectors/facts/concept-evidence/<name>/
  meta.yaml           # concept decision, semantic questions, and monitoring metadata
  signatures.yaml     # broad textual/structural signals
  ast-grep.yaml       # executable structural rules
  semgrep.yaml        # executable semantic/security rules
```

Generated detector bundles live under `../../.generated/bundles/detectors/`, including:

```text
.generated/bundles/detectors/concept-evidence/
  all.json
  questions.json
  monitoring.json
```
