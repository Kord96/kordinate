---
kind: concept
name: circuit-breaker
signatures:
  concept: circuit-breaker
  positive:
    strong:
    - explicit circuit breaker library or mesh outlier detection
    - state transition and threshold configuration
    medium:
    - failure counting plus temporary open behavior
    weak:
    - manual error counting with no recovery state
  negative:
  - retry-only logic mistaken for circuit breaker
  - no state transitions or fallback
  notes:
  - Distinguish this from retry; a circuit breaker needs stateful cutoff behavior.
source:
  memory_concept: memory/catalog/concepts/circuit-breaker.md
type: pattern
abstraction:
- resilience
- integration
scope: cross-cutting
status: primary
review_questions:
  threshold: 6
  entries:
  - id: circuit-breaker-state
    prompt: Is there explicit open or half-open state behavior rather than only retries?
    weight: 3
    signals:
    - CircuitBreaker
    - half-open
    - outlierDetection
  - id: circuit-breaker-fallback
    prompt: Is fallback or degraded behavior defined when the circuit opens?
    weight: 2
    signals:
    - fallback
    - degrade
  - id: circuit-breaker-thresholds
    prompt: Are failure thresholds and recovery timing explicitly configured?
    weight: 1
    signals:
    - failure threshold
    - recovery timeout
monitoring:
  applies_to:
  - component
  - dependency
  health_signals:
  - name: circuit.open.rate
    description: Rate of circuit transitions to open state.
  - name: fallback.activation.rate
    description: Frequency of fallback or degraded-mode activation when the circuit
      opens.
  - name: dependency.error.rate
    description: Downstream failure rate that should correlate with circuit activation.
  business_metrics: []
  gaps:
  - Missing circuit state visibility makes degraded behavior hard to distinguish from
    total outage.
---

# Explanation

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
