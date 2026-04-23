# Fact Detector Schema

This is the canonical contract for deterministic fact detectors.

Fact detectors produce normalized evidence records. They do not produce
semantic conclusions, architectural narratives, or model-authored judgments.

## Family layout

`detectors/facts/` is the family entrypoint.

The concrete fact-domain detectors currently live as flat siblings under
`detectors/`:

```text
detectors/<domain>/
  policy.yaml
  signatures.yaml
  ast-grep.yaml       # optional
  semgrep.yaml        # optional
```

Examples of `<domain>` include:
- `routes`
- `handlers`
- `boundaries`
- `events`
- `jobs`
- `auth-surface`
- `config`

Special detector families are separate:

```text
detectors/frameworks/
detectors/concepts/
```

## Detector metadata

Each fact-domain detector should declare:

```yaml
domain: <kebab-case domain id>
emits:
  - <fact kind>
frameworks:
  include: []
  exclude: []
policy:
  emit_threshold: 1 | 2 | 3 | 4 | 5
  fallback_order:
    - cpg
    - ast_grep
    - semgrep
    - signatures
    - manifest
normalization:
  fact_kind: <kind>
  required_fields: []
  optional_fields: []
```

## Guidance

Fact detectors should be:
- deterministic
- concrete
- narrow in scope
- easy to benchmark independently

If a record needs confidence, semantic uncertainty, or recommendations, it
belongs in semantic outputs, not in facts.
