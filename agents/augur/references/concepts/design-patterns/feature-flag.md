---
kind: concept
name: feature-flag
signatures:
  concept: feature-flag
  positive:
    strong:
    - runtime feature-flag SDK usage or managed flag evaluation service
    - named toggles gating production code paths
    medium:
    - environment-backed feature toggles with stable naming
    weak:
    - scattered boolean switches that may just be configuration
  negative:
  - permanent config branches mislabeled as feature flags
  - one-off debug flags with no rollout semantics
  notes:
  - Feature flags are about controlled rollout and runtime gating, not any boolean
    configuration value.
source:
  memory_concept: memory/catalog/concepts/feature-flag.md
type: pattern
abstraction:
- deployment
- design
scope: cross-cutting
status: primary
review_questions:
  threshold: 5
  entries:
  - id: feature-flag-runtime-toggle
    prompt: Are code paths gated by named runtime toggles rather than hardcoded environment
      forks?
    weight: 3
    signals:
    - feature_enabled
    - variation
    - FEATURE_
  - id: feature-flag-lifecycle
    prompt: Does the flag system appear managed as a rollout mechanism rather than
      permanent configuration?
    weight: 2
    signals:
    - LaunchDarkly
    - Unleash
    - flag
monitoring:
  applies_to:
  - component
  - flow
  health_signals:
  - name: feature_flag.evaluation.error.rate
    description: Failures resolving flag values from the flag service or local evaluator.
  - name: feature_flag.default_fallback.rate
    description: Frequency of default-value fallbacks because flag state is unavailable.
  business_metrics: []
  gaps:
  - Missing flag-evaluation visibility makes rollout and fallback behavior hard to
    trust.
---

# Explanation

## Recognition

How to identify this pattern in code.

### Signatures

- Conditional checks like `if feature_enabled("X")`, `is_feature_on()`, `hasFeature()`
- Feature flag configuration files (JSON/YAML with flag names and boolean/percentage values)
- `FEATURE_*` environment variables controlling behavior toggles
- SDK imports: LaunchDarkly (`ldclient`), Unleash (`unleash-client`), Flagsmith, Split
- Remote flag evaluation endpoints or polling for flag state changes
- Flag context objects passing user attributes for targeting rules

### Confidence

- **high** -- feature flag SDK initialized with flag evaluation calls gating code paths, plus a flag management config or service
- **medium** -- `FEATURE_*` env vars or config-file-driven toggles controlling conditional branches
- **low** -- simple boolean config values that enable/disable behavior but lack flag lifecycle management

## Architecture

Look for code paths gated by externally managed toggles with clean separation between flagged and unflagged behavior.

### Review Checklist

- Flags have clear ownership and a planned removal date (no permanent feature flags)
- Flag evaluation has a sensible default when the flag service is unavailable
- Code paths for both flag states are tested independently
- Flag naming convention is consistent and descriptive
- Stale flags are tracked and cleaned up regularly
- Targeting rules are reviewed for correctness (percentage rollouts, user segments)

### Anti-patterns

- Flags that never get removed, accumulating permanent conditional complexity
- Nested feature flags creating combinatorial explosion of code paths
- Using feature flags for configuration that should be in application config
- No default behavior when the flag service is unreachable

### Relationship To Other Concepts

- Related to [blue-green](/concepts/blue-green) and [canary](/concepts/canary) because all three are release-control mechanisms, though feature flags gate behavior independently from deployment topology or traffic shifting.
- Related to [config-management](/concepts/config-management) because flags are often managed as dynamic configuration, though they carry distinct lifecycle and cleanup concerns.

### Boundary

Use `feature-flag` when runtime behavior is intentionally gated behind named toggles that can be enabled selectively by environment, cohort, or rollout policy.

Do not use it for every configuration value. The important signal is controlled conditional behavior with rollout semantics and eventual cleanup expectations.
