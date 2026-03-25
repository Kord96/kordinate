---
description: Saga architectural pattern
curated: true
scope: global
---
# Saga


## Architecture

Look for correct compensation logic and failure handling across distributed steps.

### Review Checklist

- Each step has a corresponding compensating action
- Compensation is idempotent (safe to retry on partial failure)
- Saga coordinator tracks step state (pending, completed, compensated)
- Timeout handling exists for steps that may hang

### Anti-patterns

- Missing compensation for one or more steps (partial rollback)
- Compensating actions that can themselves fail without retry
- Using sagas where a simple two-phase operation would suffice

## Monitoring

Track distributed transaction outcomes and compensation events.

### Key Metrics

- `saga_completed_total` (counter) — successfully finished sagas
- `saga_failed_total` (counter) — sagas that triggered compensation
- `saga_compensation_total` (counter) — individual compensation steps executed
- `saga_duration_seconds` (histogram) — end-to-end saga duration
- `saga_step_duration_seconds` (histogram) — per-step latency to find bottlenecks

### Alerts

- Saga failure rate exceeding threshold
- Compensation failures (compensation step itself failed)
- Saga duration exceeding expected SLA
- Stuck sagas (started but neither completed nor compensated)

## Deployment

TODO

## Testing

TODO
