---
description: Ddd architectural pattern
curated: true
scope: global
preloaded: none
---
# Domain-Driven Design (DDD)


## Architecture

Look for clear bounded context boundaries with no leaking of internal models.

### Review Checklist

- Each bounded context owns its data and exposes only domain events or APIs
- Aggregates enforce invariants — no external code mutates aggregate state directly
- Ubiquitous language is consistent within a context (naming matches domain terms)
- Anti-corruption layers translate between contexts — no shared domain objects
- Context map exists documenting upstream/downstream relationships

### Anti-patterns

- Shared database tables across bounded contexts
- Domain objects imported directly from another context's internals
- Anemic domain model — aggregates are plain data bags with logic elsewhere
- God aggregate that grows unbounded instead of splitting into sub-contexts

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
