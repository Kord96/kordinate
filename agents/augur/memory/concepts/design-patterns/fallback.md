---
kind: concept
name: fallback
signatures: {}
type: pattern
abstraction:
- resilience
scope: cross-cutting
status: supporting
family: design-patterns
---

# Explanation

## Recognition

How to identify this pattern in code.

### Signatures

- Alternate response path used when a primary dependency fails or times out
- Default values, cached results, static responses, or feature disablement on failure
- `fallback`, `default`, `degraded`, or recovery handlers adjacent to remote calls
- Circuit breaker fallback handlers or policy-driven alternate providers

### Confidence

- **high** -- explicit alternate path is defined and intentionally used for primary failure conditions
- **medium** -- some default or cached responses exist but activation conditions are inconsistent
- **low** -- generic catch-and-return-default behavior exists without clear resilience intent

## Architecture

Look for a concrete backup behavior, not just a general desire to degrade gracefully.

### Review Checklist

- Fallback behavior is explicit and tested
- Consumers can distinguish fallback data from primary data when needed
- Fallback does not depend on the same failed dependency path
- Staleness and correctness tradeoffs are documented

### Anti-patterns

- Silent fallback that hides severe correctness issues
- Fallback path depending on the same unavailable resource
- One generic fallback used for every failure mode regardless of semantics

### Relationship To Other Concepts

- Related to [graceful-degradation](/concepts/graceful-degradation) because fallback is one concrete mechanism for preserving partial service.
- Related to [circuit-breaker](/concepts/circuit-breaker) when breakers route calls into alternate behavior after opening.
- Related to [cache-aside](/concepts/cache-aside) when cached responses become the backup path during upstream failure.

### Boundary

Use `fallback` when a specific alternate behavior is architecturally important on failure of the preferred path.

Do not use it for generic exception handling. The key signal is intentional alternate behavior.
