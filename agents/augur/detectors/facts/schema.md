# Fact extractor schema

This document defines detector-side files for Augur fact extraction.

Facts are stable normalized observations. They are produced by deterministic extractors and later interpreted by the concept layer.

## Purpose

Keep these responsibilities separate:

- semantic meaning lives under `memory/catalog/`
- deterministic extraction lives under `detectors/frameworks/` and `detectors/facts/`
- semantic interpretation and ambiguity resolution happen in concept inference
- generated runtime bundles live under `bundles/detectors/`

## Directory shape

```text
detectors/facts/<domain>/
  policy.yaml
  signatures.yaml
  ast-grep.yaml       # optional
  semgrep.yaml        # optional
```

## `policy.yaml`

```yaml
domain: <kebab-case domain id>
emits:
  - <fact kind>
frameworks:
  include: []
  exclude: []
  detectors:
    cpg:
      enabled: true | false
      detector_strength: 1 | 2 | 3 | 4 | 5
    ast_grep:
      enabled: true | false
      detector_strength: 1 | 2 | 3 | 4 | 5
  semgrep:
    enabled: true | false
    detector_strength: 1 | 2 | 3 | 4 | 5
  signatures:
    enabled: true | false
    detector_strength: 1 | 2 | 3 | 4 | 5
  manifest:
    enabled: true | false
    detector_strength: 1 | 2 | 3 | 4 | 5
policy:
  emit_threshold: 1 | 2 | 3 | 4 | 5
  fallback_order:
    - cpg
    - ast_grep
    - semgrep
    - signatures
    - manifest
  negative_rule_result_means: neutral
  requires_framework_context: true | false
normalization:
  fact_kind: <kind>
  required_fields: []
  optional_fields: []
```

## `signatures.yaml`

```yaml
domain: <kebab-case domain id>
positive:
  strong: []
  medium: []
  weak: []
negative: []
notes: []
```

## Guidance

Fact extractors should be:
- narrow
- framework-native where useful
- easy to benchmark independently

Examples:
- route extractor emits route facts
- ORM extractor emits model and state-store facts
- import graph extractor emits import-edge and hot-file facts
- Joern-backed extractors emit normalized call/data/slice facts rather than raw CPG output

Concept inference should consume these facts rather than re-reading raw detector matches.
