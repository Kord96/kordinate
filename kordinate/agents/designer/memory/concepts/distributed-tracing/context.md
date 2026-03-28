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

## Monitoring

Track trace pipeline health and sampling coverage to ensure traces are actually reaching the backend.

### Key Metrics

- `traces_exported_total` (counter) — traces successfully sent to the collector
- `traces_dropped_total` (counter) — traces dropped due to sampling, buffer overflow, or export failure
- `trace_export_latency_seconds` (histogram) — time to flush trace batches to the collector
- `span_count_per_trace` (histogram) — number of spans per trace to detect over-instrumentation or missing spans

### Alerts

- Trace drop rate exceeding threshold (data loss in the observability pipeline)
- Export latency spike (collector or network backpressure)
- Services with zero trace output (instrumentation broken or sampling misconfigured)

## Deployment

Maintain trace continuity across service versions during rollouts so traces are not broken mid-flight.

### Rollout Implications

- Old and new versions must propagate the same trace context headers — changing propagation format requires a two-phase rollout
- Deploy collector/agent infrastructure updates before application changes that emit new span attributes
- Rolling restarts may cause brief gaps in trace coverage — expected, but verify traces resume within one rollout cycle
- If changing sampling rates, roll out the new rate gradually to avoid overwhelming the collector

### Pre-deploy Checklist

- Verify the trace collector endpoint is reachable from the target environment
- Confirm context propagation format (W3C, B3, Jaeger) matches across all communicating services

