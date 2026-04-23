# Concept-evidence detectors

Executable source assets for concepts inference live here.

This layer is separate from the canonical reference layer:
- `memory/concepts/` describes what a concept means and carries signatures
- `detectors/concepts/` holds executable rule assets for concept detection

Suggested per-concept files:

```text
detectors/concepts/<name>/
  ast-grep.yaml       # executable structural rules
  semgrep.yaml        # executable semantic/security rules
```

Concept detector metadata is derived from the matching canonical concept reference under:

```text
memory/concepts/
```

Generated detector bundles live under `../../.generated/bundles/detectors/`, including:

```text
.generated/bundles/detectors/concepts/
  all.json
  review_questions.json
  monitoring.json
```
