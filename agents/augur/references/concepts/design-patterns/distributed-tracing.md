---
kind: concept
name: distributed-tracing
signatures: {}
source:
  memory_concept: memory/catalog/concepts/distributed-tracing.md
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

- OpenTelemetry SDK: `opentelemetry-api`, `opentelemetry-sdk`, `@opentelemetry/api`, `go.opentelemetry.io/otel`
- Span creation: `tracer.start_span()`, `tracer.startSpan()`, `tracer.Start()`
- Decorator-based instrumentation: `@trace`, `@WithSpan`, `@Traced`
- Span context propagation: `inject()`, `extract()`, `context.propagation`
- `traceparent` header in HTTP middleware or gRPC interceptors
- Baggage: `baggage.set_baggage()`, cross-service key-value propagation
- `TracerProvider` setup with exporter configuration (OTLP, Jaeger, Zipkin)
- Libraries: OpenTelemetry, Jaeger client, Zipkin, DataDog `ddtrace`, AWS X-Ray SDK

### Confidence

- **high** -- TracerProvider configured, spans created with parent-child relationships, and context propagated across service boundaries
- **medium** -- OpenTelemetry SDK imported and auto-instrumentation enabled but no manual spans
- **low** -- `traceparent` header forwarded in HTTP calls but no tracing SDK in dependencies

## Architecture

Look for consistent span creation, context propagation across service boundaries, and meaningful span attributes.

### Review Checklist

- TracerProvider is configured once at application startup with an appropriate exporter
- Every inbound request creates or continues a trace (middleware/interceptor handles extraction)
- Outbound calls (HTTP, gRPC, message publish) inject trace context into headers
- Spans include meaningful attributes: operation name, status code, error flag, key business identifiers
- Span names are low-cardinality and describe the operation, not the specific input
- Sensitive data is never added as span attributes (no tokens, passwords, or PII)

### Anti-patterns

- Creating spans without propagating context -- traces break at service boundaries
- Span-per-line instrumentation that creates thousands of spans per request with no useful structure
- Hardcoding exporter endpoints instead of using environment-based OTLP configuration
- Missing error recording on spans -- failures are invisible in trace views

### Relationship To Other Concepts

- Related to [correlation-id](/concepts/correlation-id) because trace context and correlation IDs both connect work across service boundaries, though tracing adds span structure and timing semantics.
- Related to [metrics-instrumentation](/concepts/metrics-instrumentation) because traces are often part of the broader observability stack alongside metrics.
- Related to [structured-logging](/concepts/structured-logging) when logs carry trace or span identifiers that align textual events with traces.

### Boundary

Use `distributed-tracing` when requests or operations are represented as propagated spans that can be reconstructed across service boundaries.

Do not use it for plain request IDs or local timing metrics unless there is real trace context propagation and span structure.
