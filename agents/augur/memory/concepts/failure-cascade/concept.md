---
description: Failure cascade flow — propagation of failure through dependent components
type: flow-shape
abstraction: [resilience, integration]
---
# Failure Cascade

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
