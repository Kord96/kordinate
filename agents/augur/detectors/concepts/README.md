# Concept detectors

Deterministic detector source assets live here.

This layer is separate from semantic memory:
- `memory/catalog/concepts/` describes what a concept means
- `detectors/concepts/` describes how to detect it deterministically

Suggested per-concept files:

```text
detectors/concepts/<name>/
  meta.yaml           # concept decision, semantic questions, and monitoring metadata
  signatures.yaml     # broad textual/structural signals
  ast-grep.yaml       # executable structural rules
  semgrep.yaml        # executable semantic/security rules
```

Generated detector bundles live under `../../bundles/detectors/`, including:

```text
bundles/detectors/concepts/
  all.json
  questions.json
  monitoring.json
```
