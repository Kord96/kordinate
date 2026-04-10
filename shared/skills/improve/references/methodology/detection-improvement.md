---
description: Generic methodology for improving deterministic extraction, detectors, and evidence pipelines
---

# Detection Improvement

Use this for any skill with deterministic extraction, pattern detection, or rule-driven evidence gathering.

## Layer Split

Keep these concerns separate:

- detector logic
  - how to recognize a signal
- normalized evidence/facts
  - what was found in this input
- semantic interpretation
  - what the evidence means in context

Do not let semantic inference hide weak evidence collection.

## Order Of Work

Prefer this sequence:

1. add instrumentation
2. inspect misses and false positives
3. group failures by signal family
4. improve detector quality for repeated failure families
5. tighten semantic interpretation after evidence improves

## Signal Families

When adding new detector work, think in generic families:

- registration
- handler
- dispatch/binding
- boundary/interface
- persistence/model
- routes/API
- runtime/config/auth

Do not design around one repo name. Design around recurring architectural signals.

## Quality Checks

For each new detector family, ask:

- What exact evidence should it emit?
- What repo types should it generalize across?
- What are the obvious false-positive traps?
- What downstream concepts or outputs depend on it?
- How will we know it improved precision or recall?

## Interaction With Semantic Review

Detectors should:

- auto-confirm only narrow, concrete concepts
- nominate architecture-heavy concepts as candidates
- carry enough evidence for semantic review to reason from

Detectors are the evidence floor, not the whole decision system.
