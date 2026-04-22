---
kind: concept
name: correlation-id
signatures: {}
source:
  memory_concept: memory/catalog/concepts/correlation-id.md
type: pattern
abstraction:
- observability
- integration
scope: cross-cutting
status: primary
---

# Explanation

## Recognition

How to identify this pattern in code.

### Signatures

- Request ID generation: `uuid4()`, `ulid()`, `nanoid()` for unique correlation IDs
- Header propagation: `X-Request-ID`, `X-Correlation-ID` headers on HTTP requests
- Middleware extracting or generating request IDs on incoming requests
- Structured logging with bound context: `structlog.bind(request_id=...)`, log correlation fields
- Logging context injection: `MDC.put("correlationId", id)` (Java), `contextvars` (Python)

### Confidence

- **high** -- Middleware generates/extracts correlation ID, propagates it in headers to downstream calls, and binds it to all log entries
- **medium** -- request ID header generated and logged but not propagated to downstream service calls
- **low** -- unique IDs in logs but no structured propagation or trace header handling

## Architecture

Look for consistent ID propagation across all service boundaries with structured logging that includes the correlation ID.

### Review Checklist

- Every incoming request gets a correlation ID (generated if not present, propagated if provided)
- ID is propagated to all downstream calls (HTTP headers, message queue metadata, gRPC metadata)
- Structured logs include the correlation ID in every log entry for the request lifecycle
- Correlation ID is searchable across all services in log aggregation

### Anti-patterns

- Generating a new ID at each service instead of propagating the original (breaks cross-service correlation)
- Logging the correlation ID only at entry and exit points, not in intermediate operations
- Propagating IDs in HTTP headers but not in async message payloads (losing correlation at queue boundaries)

See also: distributed-tracing

### Relationship To Other Concepts

- Related to [distributed-tracing](/concepts/distributed-tracing) because correlation IDs often provide the simpler cross-boundary linkage that full tracing later enriches with spans and timing.

### Boundary

Use `correlation-id` when one stable identifier is propagated across requests, logs, or messages to tie together work belonging to the same logical flow.

Do not use it for any local request ID unless it is intentionally propagated across service or async boundaries.
