---
description: Choreography — testing guidance
curated: true
scope: global
preloaded: none
---
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
