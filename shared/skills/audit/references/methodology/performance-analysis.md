---
description: Generic guidance for measuring latency, token cost, and bottlenecks while improving skills
---

# Performance Analysis

Improvement work should track performance explicitly. Better quality that doubles cost or runtime may still be a regression.

## Measure At Least

- wall-clock runtime
- token input
- token output
- total token cost
- success/failure rate
- timeout rate

## Prefer Stage Timing

If the skill has multiple phases, record time by stage. Typical stages:

- setup
- gather
- deterministic extraction
- semantic review
- synthesis
- validation

This makes bottlenecks actionable.

## Compare Quality And Cost Together

For each configuration, report:

- quality score
- runtime
- cost
- quality per minute
- quality per token or per cost unit

Do not optimize one axis blindly.

## Bundle And Configuration Analysis

When a skill has modes or bundles, evaluate:

- intended operating configurations
- a small exploratory matrix for interaction effects

The point is to learn which configurations are actually worth their cost.

## Interpret Carefully

If a change improved quality, ask:

- which stage got slower?
- which outputs improved?
- was the improvement stable?
- was the extra cost justified?

This is especially important when larger-context bundles or larger models are involved.
