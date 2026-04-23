---
kind: concept
name: timeout
signatures:
  concept: timeout
  positive:
    strong:
    - timeout parameter on external calls
    - context deadline propagation
    - asyncio wait_for or AbortController around real I/O
    medium:
    - timeout config objects tied to client initialization
    - explicit timeout error handling
    weak:
    - generic timeout constants with unclear application
  negative:
  - default framework timeouts with no explicit call-site control
  - timeout values defined only in unused config
  notes:
  - Favor detections tied to outbound calls over generic constants.
type: pattern
abstraction:
- resilience
- integration
scope: cross-cutting
status: primary
review_questions:
  threshold: 5
  entries:
  - id: timeout-explicit-on-external-calls
    prompt: Are timeouts explicitly configured on real external calls rather than
      only in generic config?
    weight: 3
    signals:
    - timeout=
    - wait_for(
    - AbortController
  - id: timeout-distinct-handling
    prompt: Are timeout failures handled distinctly from generic errors?
    weight: 2
    signals:
    - TimeoutError
    - DeadlineExceeded
monitoring:
  applies_to:
  - component
  - dependency
  - flow
  health_signals:
  - name: timeout.rate
    description: Rate of requests, jobs, or downstream calls that terminate due to
      timeout.
  - name: timeout.cancellation.rate
    description: Frequency of successful cancellation or cleanup when a timeout occurs.
  - name: downstream.timeout.rate
    description: Timeout rate for specific external calls or slow internal boundaries.
  business_metrics: []
  gaps:
  - Timeout handling without timeout metrics hides latency collapse until users experience
    hard failures.
family: design-patterns
---

# Explanation

## Recognition

How to identify this pattern in code.

### Signatures

- `timeout=` parameter on HTTP, gRPC, or database calls
- `context.WithTimeout` or `context.WithDeadline` (Go)
- `asyncio.wait_for(timeout=)` (Python)
- `socket.settimeout()` (Python)
- `TimeoutError` or `DeadlineExceeded` handling in catch/except blocks
- Request timeout configs (`connect_timeout`, `read_timeout`, `write_timeout`)
- Deadline propagation across service boundaries via context or headers
- `AbortController` with `setTimeout` (JavaScript)

### Confidence

- **high** -- explicit timeout parameter on every external call with corresponding error handling
- **medium** -- timeout config present but not consistently applied to all call sites
- **low** -- only default framework timeouts relied upon, no explicit timeout values in code

## Architecture

Look for explicit timeout enforcement on every external call with deadline propagation across boundaries.

### Review Checklist

- Every external call (HTTP, DB, gRPC, message broker) has an explicit timeout set
- Timeouts propagate through the call chain -- downstream deadlines are shorter than upstream
- Timeout values are configurable, not hardcoded literals
- Timeout errors are caught and handled distinctly from other failures
- Connection timeouts are separate from read/write timeouts

### Anti-patterns

- No timeout on external calls -- a hung dependency blocks the caller indefinitely
- Uniform timeout across all calls regardless of expected latency profile
- Catching timeout errors silently without logging, metrics, or fallback
- Deadline not propagated to downstream services -- child call outlives parent deadline

See also: circuit-breaker, retry (often combined)

### Relationship To Other Concepts

- Related to [circuit-breaker](/concepts/circuit-breaker) because this concept commonly appears alongside it or is clarified by contrast with it.
- Related to [retry](/concepts/retry) because this concept commonly appears alongside it or is clarified by contrast with it.

### Boundary

Use `timeout` when the important observation is this specific architectural concern within a cross-cutting architectural concern that can span multiple layers or services.

Do not use it just because a few signatures match; the surrounding responsibilities and architectural role should line up too.
