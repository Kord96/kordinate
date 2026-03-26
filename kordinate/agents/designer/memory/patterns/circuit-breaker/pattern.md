---
description: Circuit Breaker architectural pattern
curated: true
scope: global
preloaded: none
---
# Circuit Breaker


## Recognition

How to identify this pattern in code.

### Signatures

- `resilience4j` with `CircuitBreaker` and `CircuitBreakerConfig` classes (Java)
- `pybreaker` library usage (`CircuitBreaker` class, `@circuit` decorator) in Python
- `polly` with `CircuitBreakerPolicy` in .NET applications
- Hystrix `HystrixCommand` with circuit breaker configuration (legacy Java)
- Istio `DestinationRule` with `outlierDetection` settings in service mesh configuration
- `opossum` circuit breaker library in Node.js applications
- `tenacity` with stop conditions and retry state tracking (Python)

### Confidence

- **high** -- explicit circuit breaker library with configured thresholds, state transitions (closed/open/half-open), and fallback behavior
- **medium** -- retry logic with failure counting and a threshold that disables calls, but no formal state machine or half-open probing
- **low** -- try/catch around external calls with manual error counting but no automatic state transitions or recovery mechanism

## Architecture

Look for correct state machine implementation: closed -> open -> half-open.

### Review Checklist

- Failure threshold and recovery timeout are configurable, not hardcoded
- Half-open state allows a limited number of probe requests
- Circuit state is observable (logging or metrics on state transitions)
- Fallback behavior is explicitly defined (not silent swallowing)

### Anti-patterns

- Wrapping every call in a circuit breaker (only external dependencies need them)
- No fallback — circuit opens and the caller gets raw exceptions
- Shared circuit state across unrelated dependencies

## Monitoring

Track circuit state transitions and dependency failure rates.

### Key Metrics

- `circuit_state` (gauge) — current state per dependency (0=closed, 1=open, 2=half-open)
- `circuit_failures_total` (counter) — failure count that drives the breaker
- `circuit_open_duration_seconds` (histogram) — how long circuits stay open before recovery
- `circuit_recovery_success_total` (counter) — successful half-open probes

### Alerts

- Circuit open for longer than expected recovery window
- High failure rate approaching breaker threshold (early warning)
- Repeated open-close cycling (flapping dependency)

## Deployment

Consider dependency health and connection draining during rollouts.

### Rollout Implications

- Drain existing connections before terminating pods — open circuits may not recover if pod dies mid-request
- Health gate: do not mark new pods as ready until circuit breakers for critical dependencies are in closed state
- Rolling restart may temporarily spike circuit opens — expected, but monitor for cascading failures
- If a dependency is already degraded, pause rollout to avoid all pods opening circuits simultaneously

### Pre-deploy Checklist

- Verify circuit breaker recovery timeouts are shorter than readiness probe intervals
- Check that pod terminationGracePeriodSeconds allows in-flight requests to complete

## Testing

Test the full state machine lifecycle and verify fallback behavior activates correctly at each transition.

### Unit Tests

- Verify closed-to-open transition: inject failures up to the threshold and assert the circuit opens on the next failure
- Test half-open behavior: after recovery timeout, assert exactly the configured number of probe requests are allowed through
- Verify open-to-closed transition: successful probes in half-open state return the circuit to closed
- Assert fallback is invoked when the circuit is open — callers receive the fallback response, not an exception

### Integration Tests

- Wire a circuit breaker around a real dependency, degrade the dependency, and verify the breaker opens and closes as expected
- Test that circuit state is per-dependency — degrading one dependency does not open the breaker for another
- Verify metrics emission: state transitions, failure counts, and recovery probes all emit correct metric values

### Failure Injection

- Simulate a flapping dependency (alternating success/failure) and verify the circuit does not oscillate rapidly between states
- Inject total dependency failure and verify the circuit opens, then restore the dependency and confirm recovery through half-open probes
- Introduce latency exceeding the timeout threshold and verify slow responses count as failures toward the breaker threshold
