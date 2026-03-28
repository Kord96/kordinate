## Testing

Validate that aggregates enforce invariants and bounded contexts remain isolated through their public contracts.

### Unit Tests

- Test aggregate invariants by attempting illegal state transitions and asserting they are rejected
- Verify that domain events are published with correct data when aggregate state changes
- Test value objects for equality semantics and validation rules (e.g., invalid email rejected at construction)
- Assert that factory methods produce aggregates in a valid initial state

### Integration Tests

- Test anti-corruption layer translations — send upstream context events and verify downstream context receives correctly mapped domain objects
- Verify that domain events published by one aggregate are consumed and handled by other aggregates without shared internal state
- Test repository implementations against the actual store, asserting aggregate reconstitution preserves invariants

### Failure Injection

- Simulate anti-corruption layer failure and verify the downstream context rejects or queues rather than accepting corrupted data
- Inject duplicate domain events and confirm aggregate handlers are idempotent
- Simulate repository write failure mid-aggregate-update and verify no partial state is persisted

## Monitoring

Track aggregate operations and cross-context communication to detect boundary violations and performance issues.

### Key Metrics

- `aggregate_command_total` (counter) — commands processed per aggregate type
- `domain_event_published_total` (counter) — events published per bounded context
- `cross_context_call_total` (counter) — calls between bounded contexts (should be low and intentional)
- `aggregate_command_duration_seconds` (histogram) — time to process commands per aggregate type
- `anti_corruption_translation_errors_total` (counter) — failures in anti-corruption layer translations

### Alerts

- Cross-context call rate increasing unexpectedly (boundary erosion)
- Aggregate command latency exceeding SLA
- Event publishing failures accumulating in any context
- Anti-corruption layer error rate exceeding threshold

## Deployment

Bounded context boundaries and aggregate schema changes require careful coordination during rollouts.

### Rollout Implications

- Aggregate schema changes need database migrations applied before new code rolls out — never deploy code expecting a schema that does not yet exist
- Deploying a bounded context that emits new domain events requires downstream consumers to handle unknown event fields gracefully
- Anti-corruption layer changes must be backward-compatible — old and new versions of the ACL may run simultaneously during rollout
- Shared-nothing contexts can deploy independently, but contexts with synchronous dependencies need ordered rollouts

### Pre-deploy Checklist

- Verify database migrations for aggregate schema changes are applied and backward-compatible
- Confirm downstream bounded contexts can tolerate new or changed domain events
- Check that anti-corruption layer translations handle both old and new upstream formats

