---
description: Timeout architectural pattern
type: pattern
testable: true
observable: true
distributed: true
curated: true
scope: global
preloaded: none
graphable: true
abstraction: [resilience, integration]
---
# Timeout

## Recognition

How to identify this pattern in code.

### Signatures

- `timeout=` parameter explicitly configured on HTTP, gRPC, or database calls
- `context.WithTimeout` or `context.WithDeadline` (Go) wrapping call sites
- `asyncio.wait_for(timeout=)` (Python), `socket.settimeout()` (Python)
- `TimeoutError` or `DeadlineExceeded` handling in catch/except blocks with recovery logic
- Explicit timeout configs: `connect_timeout`, `read_timeout`, `write_timeout`, `statement_timeout`
- Deadline propagation across service boundaries via context or headers (`grpc-timeout`, `X-Request-Timeout`)
- `AbortController` + `AbortSignal.timeout()` for fetch/request cancellation (JavaScript)

**Not this pattern:** `setTimeout()` used for scheduling delayed execution (e.g., debouncing, animations, polling) is not the timeout resilience pattern. The timeout pattern is about protecting against hung external calls by enforcing a maximum wait time. Also, idle timeouts on connection pools or session expiry are lifecycle management, not the timeout resilience pattern.

### Confidence

- **high** -- explicit timeout parameter on every external call with corresponding timeout error handling and recovery
- **medium** -- timeout config present on external calls but not consistently applied to all call sites
- **low** -- only default framework timeouts relied upon, no explicit timeout values in application code

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
