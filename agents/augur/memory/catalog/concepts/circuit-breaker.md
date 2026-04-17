---
description: Circuit Breaker architectural pattern
type: pattern
testable: true
observable: true
distributed: true
graphable: true
abstraction:
- resilience
- integration
status: primary
scope: cross-cutting
relationships:
  related_to:
  - timeout
  - retry
  - bulkhead
aliases: []
disambiguates_from: []
preferred_over: []
implies: []
anti_signals: []
detector_coverage: rich
examples: []
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

### Relationship To Other Concepts

- Related to [timeout](/concepts/timeout) because circuit breakers usually depend on bounded failure detection and call deadlines.
- Related to [retry](/concepts/retry) because retries are often paired with breakers, but careless retry behavior can also keep a breaker open longer.
- Related to [bulkhead](/concepts/bulkhead) because both isolate failure, though a breaker trips on unhealthy dependencies while a bulkhead partitions capacity.

### Boundary

Use `circuit-breaker` when calls to an external dependency are explicitly short-circuited after repeated failure to protect the caller and the dependency.

Do not use it for generic retries, timeouts, or health checks unless there is explicit open/half-open/closed failure gating behavior.
