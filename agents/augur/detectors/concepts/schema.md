# Concept detector schema

This document defines the detector-side files for Augur concepts.

## Purpose

Concept detection is deterministic runtime machinery and should be kept separate from semantic memory.

- semantic meaning lives under `memory/catalog/concepts/`
- deterministic detection lives under `detectors/concepts/`
- generated execution bundles live under `bundles/detectors/`

## Directory shape

```text
detectors/concepts/<name>/
  meta.yaml           # decision rules, semantic questions, monitoring guidance
  signatures.yaml     # broad textual/structural signals
  ast-grep.yaml       # optional executable structural rules
  semgrep.yaml        # optional executable semantic/security rules
```

## `meta.yaml`

```yaml
concept: <kebab-case concept id>
detectors:
  ast_grep:
    enabled: true | false
    detector_strength: 1 | 2 | 3 | 4 | 5
  semgrep:
    enabled: true | false
    detector_strength: 1 | 2 | 3 | 4 | 5
  signatures:
    enabled: true | false
    detector_strength: 1 | 2 | 3 | 4 | 5
  questions:
    enabled: true | false
    detector_strength: 1 | 2 | 3 | 4 | 5
    ask_when:
      - noisy_rule_match
      - conflicting_evidence
      - broad_match
      - low_rule_confidence
      - architecture_level_concept
policy:
  auto_confirm:
    allowed: true | false
    min_detector_strength: 1 | 2 | 3 | 4 | 5
    min_match_confidence: 1 | 2 | 3 | 4 | 5
    requires_no_contradiction: true | false
  unresolved_state: candidate | inconclusive
  negative_rule_result_means: neutral
  broad_match_requires_questions: true | false
questions:
  threshold: <integer>
  entries:
    - id: <stable id>
      prompt: <question text>
      weight: <integer>
      signals: []
monitoring:
  applies_to: []
  health_signals:
    - name: <metric name>
      description: <what health condition this signal helps detect>
  business_metrics:
    - name: <metric name>
      description: <what business outcome this metric measures>
  gaps: []
```

## `signatures.yaml`

```yaml
concept: <kebab-case concept id>
positive:
  strong: []
  medium: []
  weak: []
negative: []
notes: []
```

## Guidance

Keep the split clean:
- semantic meaning stays with the concept semantics side
- concept decision/questions/monitoring metadata live in `meta.yaml`
- broad textual clues live in `signatures.yaml`
- executable AST/semgrep rules remain standalone detector artifacts
