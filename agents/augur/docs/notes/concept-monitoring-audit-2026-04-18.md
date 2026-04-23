# Concept Monitoring Audit 2026-04-18

Focused audit of how concept metadata currently contributes to health and business expectations.

## Current State

The plumbing already exists:
- concept detector `meta.yaml` files carry `monitoring`
- detector bundles compile concept monitoring into `.generated/bundles/detectors/concept-evidence/monitoring.json`
- `synthesize_atlas_from_facts.py` projects concept monitoring into:
  - component health
  - external dependency health
  - flow health
  - flow business metrics

So the system does not need to be invented from scratch.

## Main Problems

### 1. Monitoring projection trusted concepts too broadly

Before tightening, any selected concept pattern could project monitoring expectations.
That meant broad concepts like `rest`, `event-driven`, `scheduler`, and loosely inferred `workflow-engine` could attach health expectations even when the concept itself was only a weak candidate.

This is now tightened in code:
- monitoring projection is allowed only for concepts that are strong enough to justify it
- weak or broad semantic-review candidates no longer project monitoring by default

### 2. Business metrics are effectively absent

Current detector metadata is almost entirely health-signal oriented.
A scan of `detectors/facts/concept-evidence/*/meta.yaml` found:
- many concepts define `health_signals`
- `business_metrics` is currently empty across the active concept metadata set

So concept metadata can currently improve operational health expectations, but not business-logic expectations in a meaningful way.

### 3. Applies-to scopes are broad but not confidence-aware

Many concept metadata entries declare `applies_to` for:
- `component`
- `flow`
- `dependency`

That is useful, but without confidence gating it can over-project generic expectations.

## What Looks Useful Right Now

### Stronger operational concepts
These are good candidates to keep projecting health expectations when detector backing is strong enough:
- `repository`
- `timeout`
- `retry`
- `circuit-breaker`
- `health-check`
- `cache-aside`
- `outbox`

These concepts naturally imply observable operational risks.

### Weaker or broader concepts
These should not drive strong monitoring expectations unless later confirmed more rigorously:
- `rest`
- `event-driven`
- `scheduler`
- `service-manager`
- `state-machine`
- broad `workflow-engine`

These concepts are often real, but their presence alone does not justify strong projected monitoring expectations.

## Code Change Applied

`agents/augur/scripts/synthesis/synthesize_atlas_from_facts.py`

Monitoring projection now requires concept eligibility:
- `confirmed` verdicts always eligible
- strong detector-backed concepts with enough confidence may project
- partial concepts only project at high confidence
- weak detector-backed concepts do not project by default
- semantic-review concepts do not project by default unless they are detector-strong and high-confidence

Practical result on the active concept set:
- `repository` -> eligible
- `timeout` -> eligible
- `rest` -> not eligible by default
- `workflow-engine` -> not eligible by default
- `event-driven` -> not eligible by default
- `scheduler` -> not eligible by default

## Recommended Next Steps

1. Keep using concepts for health expectations first.
- this path already exists and now has better confidence gating

2. Add business metrics only for concepts where they are genuinely clear.
Start with:
- `workflow-engine`
  - completion rate
  - time to completion
  - failure by step or stage
- `scheduler`
  - jobs completed per interval
  - missed runs
  - backlog cleared per run
- `repository`
  - write success rate
  - stale read rate only if caches or replicas are involved
- `event-driven`
  - end-to-end event completion rate
  - publish-to-consume latency

3. Keep business metrics concept-specific and sparse.
- do not add generic business metrics to every concept
- only add them where the concept strongly implies a business-facing throughput or completion model

4. Tie future concept monitoring expectations to concept provenance.
- detector backing
- decision mode
- final semantic verdict

## Bottom Line

Concepts can absolutely add value for health and business expectations.
But the current system was stronger on health than business, and it was projecting expectations too broadly.

After the tightening change, the path is better:
- concepts can still drive operational expectations
- weak or broad concepts no longer do so automatically
- the next real opportunity is to add a small, high-signal set of business metrics for the few concepts where they are actually meaningful
