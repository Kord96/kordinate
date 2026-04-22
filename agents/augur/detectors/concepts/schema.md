# Concepts Detector Schema

This document defines the detector-side executable files for Augur concepts.

## Purpose

Concept detection is deterministic runtime machinery and should be kept separate from the canonical reference layer.

- semantic meaning and signatures live under the semantic family subdirectories in `references/concepts/`
- deterministic executable rules live under `detectors/concepts/`
- generated execution bundles live under `.generated/bundles/detectors/`

## Directory shape

```text
detectors/concepts/<name>/
  ast-grep.yaml       # optional executable structural rules
  semgrep.yaml        # optional executable semantic/security rules
```

## Matching reference under `references/concepts/`

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
signatures:
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
- semantic meaning and signatures stay with the canonical references side
- executable AST/semgrep rules remain standalone detector artifacts under `detectors/concepts/`
