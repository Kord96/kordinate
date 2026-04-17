---
description: Graceful Degradation architectural pattern
type: pattern
testable: true
observable: true
distributed: true
graphable: true
abstraction:
- resilience
- lifecycle
status: primary
scope: cross-cutting
relationships:
  related_to:
  - circuit-breaker
  - fallback
  - health-check
aliases: []
disambiguates_from: []
preferred_over: []
implies: []
anti_signals: []
detector_coverage: partial
examples: []
---
# Graceful Degradation

## Recognition

How to identify this pattern in code.

### Signatures

- Fallback responses returned when a dependency is down or slow
- Reduced functionality mode toggled by health state or feature flags
- Cached responses served as fallback when the live source is unavailable
- `try/except` or `try/catch` blocks returning a default value instead of propagating errors
- Feature flags disabling non-essential features under load
- Circuit breaker fallback handlers providing degraded responses
- Graceful error pages or partial-content responses to the client

### Confidence

- **high** -- explicit fallback paths defined per dependency with documented degraded behavior
- **medium** -- some fallback logic exists but not consistently applied across all dependencies
- **low** -- generic error handling that returns defaults but without intentional degradation strategy

## Architecture

Look for intentional fallback paths that keep the system usable when dependencies fail.

### Review Checklist

- Each non-critical dependency has a defined fallback behavior (cache, default, omit)
- Critical vs non-critical dependencies are explicitly classified
- Degraded mode is observable -- logs and metrics indicate when fallbacks activate
- Fallback responses are clearly distinguishable from normal responses (e.g., staleness indicators)
- System recovers automatically when the dependency comes back

### Anti-patterns

- All-or-nothing failure -- one dependency down takes the entire service offline
- Silent degradation where clients receive stale data without any indication
- Fallback logic that itself depends on the failing service
- No testing of degraded paths -- fallback code rots and fails when actually needed

### Relationship To Other Concepts

- Related to [circuit-breaker](/concepts/circuit-breaker) because breakers often trigger or protect degraded modes.
- Related to [fallback](/concepts/fallback) because fallback behavior is one of the common mechanisms used to degrade gracefully.
- Related to [health-check](/concepts/health-check) when degraded states are surfaced explicitly for operators or traffic controllers.

### Boundary

Use `graceful-degradation` when the system intentionally preserves partial service or reduced capability instead of failing completely when a dependency or feature path is unavailable.

Do not use it for silent breakage or generic exception handling. The key signal is deliberate partial-service design.
