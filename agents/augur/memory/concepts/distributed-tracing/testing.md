---
description: Distributed Tracing Instrumentation — testing guidance
type: supplementary
---
## Testing

Verify that trace context propagates across service boundaries and that spans form a complete, connected tree.

### Unit Tests

- Assert that outgoing HTTP/gRPC calls include trace context headers (traceparent, b3, etc.)
- Verify that incoming requests with trace headers create child spans rather than new root spans
- Test that span attributes (service name, operation, status) are populated correctly
- Assert that sensitive data is not recorded in span attributes or logs attached to traces

### Integration Tests

- Issue a request that crosses two or more services and verify the resulting trace contains spans from all services in a single tree
- Test that async operations (message queues, background jobs) propagate trace context and appear in the same trace
- Verify that error spans include the correct status code and error message without leaking stack traces

### Pipeline Tests

- Send traces to a test collector and verify they arrive with expected structure and latency
- Test sampling configuration: head-based and tail-based sampling should include/exclude traces at the configured rates
