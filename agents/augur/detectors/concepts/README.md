# Concept-evidence detectors

Executable source assets for concepts inference live here.

This layer is separate from the canonical reference layer:
- `memory/concepts/` describes what a concept means and carries signatures
- `detectors/concepts/` holds executable rule assets for concept detection

Concept assets are organized by detector mechanism:

```text
detectors/concepts/
  policy.yaml
  ast-grep/<name>.yaml
  semgrep/<name>.yaml
  signatures/<name>.yaml
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
