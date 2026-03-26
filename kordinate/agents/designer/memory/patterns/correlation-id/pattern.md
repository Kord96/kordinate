---
description: Correlation ID / Distributed Tracing architectural pattern
curated: true
scope: global
preloaded: none
---
# Correlation ID / Distributed Tracing

## Recognition

How to identify this pattern in code.

### Signatures

- Request ID generation and propagation: `X-Request-ID`, `X-Correlation-ID` headers
- W3C trace context: `traceparent`, `tracestate` headers
- Span creation and context propagation in service-to-service calls
- Libraries: OpenTelemetry (`opentelemetry-api`, `@opentelemetry/sdk-trace-node`), Jaeger client, Zipkin
- Structured logging with bound context: `structlog.bind(request_id=...)`, log correlation fields
- Middleware extracting or generating trace/request IDs on incoming requests
- Trace exporters configured to send spans to a collector (Jaeger, Zipkin, OTLP endpoint)

### Confidence

- **high** -- OpenTelemetry SDK initialized with span creation, context propagation across service boundaries, and a trace collector endpoint
- **medium** -- request ID header generated and logged but not propagated to downstream service calls
- **low** -- unique IDs in logs but no structured propagation or trace header handling

## Architecture

Look for consistent ID propagation across all service boundaries with structured logging that includes trace context.

### Review Checklist

- Every incoming request gets a correlation ID (generated if not present, propagated if provided)
- ID is propagated to all downstream calls (HTTP headers, message queue metadata, gRPC metadata)
- Structured logs include the correlation ID in every log entry for the request lifecycle
- Trace context follows W3C standard (`traceparent`) for interoperability
- Sampling strategy is configured appropriately (not 100% in production for high-traffic services)
- Trace data is searchable by correlation ID across all services

### Anti-patterns

- Generating a new ID at each service instead of propagating the original (breaks cross-service correlation)
- Logging the correlation ID only at entry and exit points, not in intermediate operations
- No sampling strategy (tracing 100% of requests in production causes storage and performance overhead)
- Propagating IDs in HTTP headers but not in async message payloads (losing trace context at queue boundaries)
