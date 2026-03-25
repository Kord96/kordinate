---
description: Choreography architectural pattern
curated: true
scope: global
preloaded: none
---
# Choreography


## Architecture

Look for clear event contracts and no hidden coupling between services.

### Review Checklist

- Event schemas are versioned and documented — consumers know what to expect
- Each service can be deployed independently without breaking the chain
- Event flows are traceable end-to-end (correlation IDs in every event)
- Failure in one service does not silently stall the entire workflow

### Anti-patterns

- Implicit ordering assumptions — Service B assumes A always fires first
- Event ping-pong — two services triggering each other in a loop
- No observability — impossible to reconstruct what happened from logs alone
- Choreography used where a saga/orchestrator would be clearer (too many steps)

## Monitoring

Track event flow across services and dead-letter accumulation to detect broken chains and stalled workflows.

### Key Metrics

- `event_published_total` (counter) — events emitted per service and event type
- `event_consumed_total` (counter) — events processed per consuming service
- `event_processing_duration_seconds` (histogram) — time from event receipt to processing completion
- `dead_letter_events_total` (counter) — events that failed processing and landed in dead-letter
- `event_flow_lag_seconds` (gauge) — end-to-end delay from first event to final outcome per correlation ID

### Alerts

- Published-to-consumed event ratio diverging (events being dropped or not consumed)
- Dead-letter queue depth growing without remediation
- Event processing latency exceeding SLA for any service in the chain
- Correlation IDs with no terminal event within expected time window (stalled workflows)

## Deployment

Event schema versioning and consumer deployment ordering determine whether the event chain breaks during rollout.

### Rollout Implications

- Deploy consumers before producers when introducing new event fields — consumers must be able to handle the new schema before events arrive
- Event schema changes must be backward-compatible (additive only) since old and new consumers run simultaneously during rollout
- Deploying a producer that emits a new event type before any consumer exists creates unprocessed event buildup
- Rolling back a single service may break the choreography if other services have already adapted to its new event schema

### Pre-deploy Checklist

- Verify event schema changes are backward-compatible (no removed or renamed fields)
- Confirm all downstream consumers are deployed and ready before upstream producers emit new event types
- Check that correlation ID propagation is intact across all services involved in the rollout

## Testing

Validate event contracts between services and ensure each participant can be tested and deployed independently.

### Unit Tests

- Test each service's event handler in isolation — given an input event, assert the correct output event or state change
- Verify event schema compliance: validate produced events against the published contract (required fields, types, version)
- Test that services handle unknown event fields gracefully (forward compatibility)
- Assert correlation ID propagation — every output event carries the correlation ID from the input event

### Integration Tests

- Deploy two adjacent services and verify the end-to-end event flow between them produces the expected outcome
- Test independent deployability: upgrade one service's event version and verify downstream consumers still function
- Run the full choreographed workflow end-to-end and verify the final system state using correlation ID tracing

### Failure Injection

- Stop a downstream consumer and verify upstream services continue operating without blocking or failing
- Inject a malformed event and verify the consuming service rejects it to dead-letter without crashing the pipeline
- Simulate event broker unavailability and confirm services buffer or retry rather than silently dropping events
