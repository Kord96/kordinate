---
description: Generic guidance for designing trustworthy evals and benchmarks for skills and agents
---

# Eval Design

## Principles

- Prefer realistic tasks over synthetic trivia.
- Prefer explicit expectations over vibe-based judging.
- Measure false positives, not just misses.
- Use repeated runs when model variance matters.
- Separate hard validation from qualitative comparison.

## Eval Layers

Use the smallest layer that answers the question:

- Trigger eval
  - Should this skill activate at all?
- Prompt/task eval
  - Can the skill perform the task?
- Benchmark
  - How stable, fast, and effective is it across repeated runs?
- Dataset benchmark
  - How does it perform across a portfolio of inputs?

## Assertion Design

Good assertions are:

- checkable
- specific
- tied to observable outputs
- discriminative between strong and weak behavior

Bad assertions are:

- broad correctness claims
- subjective praise
- things every model trivially satisfies

## Comparative Design

When doing A/B or model comparisons:

- keep prompt shape aligned
- keep input data aligned
- keep retries/timeouts aligned
- record cost and latency alongside quality
- use blind comparison for presentation-heavy outputs

## Variance

Use repeated runs when:

- stochastic model output matters
- output quality is close between configurations
- latency or cost instability matters

Single-run wins are weak evidence.

## Human Review

Use human review for:

- surprising benchmark results
- high-impact failures
- benchmark label disputes
- architecture-level judgments that are hard to codify

The goal is not to replace automation. It is to keep the benchmark honest.
