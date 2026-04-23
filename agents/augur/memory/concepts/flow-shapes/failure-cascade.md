---
kind: concept
name: failure-cascade
signatures: {}
type: flow-shape
abstraction:
- resilience
- integration
scope: cross-cutting
status: primary
family: flow-shapes
---

# Explanation

## Recognition

### Signatures

- Component A depends on B depends on C — if C fails, B fails, then A fails
- No circuit breakers or timeouts on dependency calls
- Synchronous call chains where one slow/failed service blocks the caller
- Thread pool exhaustion from blocked calls propagating up the chain
- Database connection pool exhaustion causing cascading timeouts
- Retry storms: failed service recovers but gets overwhelmed by queued retries
- Health check endpoints that don't distinguish between own health and dependency health
- Missing fallback or degraded-mode behavior when dependencies are unavailable

### Confidence

- **high** — documented or observable chain where component failure propagates through multiple dependents with no isolation
- **medium** — synchronous dependency chain without circuit breakers, but failure hasn't been observed yet
- **low** — dependency chain exists but has some resilience patterns (retries, timeouts) that may or may not prevent cascading

### Relationship To Other Concepts

- Related to [circuit-breaker](/concepts/circuit-breaker), [bulkhead](/concepts/bulkhead), and [graceful-degradation](/concepts/graceful-degradation) because those patterns are common mitigations against cascading failure.

### Boundary

Use `failure-cascade` when the architecture allows one component failure to propagate through dependent components and amplify into a wider outage.

Do not use it for isolated failures or single-service outages. The defining property is propagation across dependencies.
