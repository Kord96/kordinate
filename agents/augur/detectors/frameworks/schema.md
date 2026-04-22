# Framework Detector Schema

This document defines deterministic framework detection assets.

## Purpose

Framework detection establishes stack context and narrows the concept search space before concept detection runs.

- framework semantics and signatures live under `references/frameworks/`
- generated execution bundles live under `.generated/bundles/detectors/frameworks/`

## Directory shape

```text
references/frameworks/<name>.md
```

## `references/frameworks/<name>.md`

```yaml
---
kind: framework
name: <name>
signatures:
  framework: <name>
  manifest_packages:
    package_json: []
    pyproject: []
    requirements: []
    gemfile: []
    composer: []
    cargo: []
    pom: []
    go_mod: []
    package_swift: []
    mix_exs: []
  source_extensions: []
  path_patterns:
    strong: []
    medium: []
    weak: []
  source_patterns:
    strong: []
    medium: []
    weak: []
  negative_path_patterns: []
  negative_source_patterns: []
---

# Explanation
```

## Runtime role

Framework detection should run before concept detection and should influence:
- category prioritization
- which detector bundles are loaded
- API review and framework-native expectations

`references/frameworks/` is the canonical detector-facing and skill-facing reference layer.
