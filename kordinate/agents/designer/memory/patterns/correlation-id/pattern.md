---
description: Correlation ID architectural pattern
type: pattern
testable: true
observable: true
distributed: true
curated: true
scope: global
preloaded: none
---
# Correlation ID

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
