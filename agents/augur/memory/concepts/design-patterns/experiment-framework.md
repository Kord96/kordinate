---
kind: concept
name: experiment-framework
signatures: {}
type: pattern
abstraction:
- deployment
- ml
scope: cross-cutting
status: primary
family: design-patterns
---

# Explanation

## Recognition

How to identify this pattern in code.

### Signatures

- Experiment assignment logic: users bucketed into control/treatment variants
- Methods like `assign_variant()`, `get_variant()`, `track_metric()`, `is_in_experiment()`
- Experiment configuration defining variants, traffic allocation, and target population
- Metric collection per variant with statistical significance checks
- Feature flag integration gating code paths by experiment variant
- Hash-based or random assignment ensuring consistent bucketing per user
- Libraries: Statsig, LaunchDarkly, Optimizely, GrowthBook, Unleash, custom frameworks

### Confidence

- **high** — `assign_variant()`/`track_metric()` calls with experiment configs, bucketing logic, and significance analysis
- **medium** — feature flags with variant-specific metric tracking and traffic percentage allocation
- **low** — conditional code paths toggled by user segment with separate metric counters

## Architecture

Look for a system that assigns users to experiment variants, tracks per-variant metrics, and evaluates statistical significance.

### Review Checklist

- Assignment is deterministic per user (same user always gets the same variant for a given experiment)
- Metrics are tracked per variant with enough granularity for statistical analysis
- Experiment configuration is separate from application code (external config or service)
- Sample size and duration are planned to reach statistical significance
- Interaction effects between concurrent experiments are considered (mutual exclusion or layering)
- Experiments have clear start/end criteria and cleanup process for concluded experiments

### Anti-patterns

- Non-deterministic assignment causing users to flip between variants across sessions
- Tracking only aggregate metrics with no per-variant breakdown
- No sample size planning, ending experiments before reaching significance
- Leaving concluded experiment code paths in production indefinitely

### Relationship To Other Concepts

- Related to [feature-flag](/concepts/feature-flag) because many experiment systems use flag-based variant assignment as one delivery mechanism.
- Related to [metrics-instrumentation](/concepts/metrics-instrumentation) because experiments only become useful when outcomes are measured consistently.
- Related to [model-registry](/concepts/model-registry) when experiments compare model variants or route traffic across model versions.

### Boundary

Use `experiment-framework` when the system has explicit infrastructure for assigning variants, collecting outcomes, and evaluating experiment results.

Do not use it for ad hoc feature toggles or one-off A/B tests without a broader experiment lifecycle.
