# Framework detector schema

This document defines deterministic framework detection assets.

## Purpose

Framework detection establishes stack context and narrows the concept search space before concept detection runs.

- framework semantics live under `memory/catalog/frameworks/`
- framework detectors live under `detectors/facts/frameworks/`
- generated execution bundles live under `.generated/bundles/detectors/frameworks/`

## Directory shape

```text
detectors/facts/frameworks/<name>/
  policy.yaml
  signatures.yaml
  ast-grep.yaml      # optional
  semgrep.yaml       # optional
```

## `policy.yaml`

```yaml
framework: <name>
policy:
  auto_confirm:
    allowed: true | false
    min_signal_strength: weak | medium | strong
  unresolved_state: candidate | inconclusive
```

## `signatures.yaml`

```yaml
framework: <name>
signals:
  strong: []
  medium: []
  weak: []
negative_signals: []
```

## Runtime role

Framework detection should run before concept detection and should influence:
- category prioritization
- which detector bundles are loaded
- API review and framework-native expectations

`memory/catalog/frameworks/index.md` is a supporting cross-language reference, not the canonical detector contract.
