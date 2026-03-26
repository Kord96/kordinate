---
description: Circuit Breaker architectural pattern
type: pattern
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
