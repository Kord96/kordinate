---
description: State Machine — monitoring guidance
---
## Monitoring

Track state distributions, transition activity, and stuck entities to ensure the machine progresses correctly.

### Key Metrics

- `state_machine_transitions_total` (counter) — transitions partitioned by source state, event, and target state
- `state_machine_rejected_transitions_total` (counter) — invalid transition attempts (caller sending wrong events)
- `state_machine_state_duration_seconds` (histogram) — time entities spend in each state before transitioning
- `state_machine_entities_by_state` (gauge) — count of entities currently in each state
- `state_machine_concurrent_transition_attempts_total` (counter) — simultaneous transitions on the same entity (race indicator)
- `state_machine_guard_failures_total` (counter) — guard condition evaluation failures per transition

### Alerts

- Entity stuck in a non-terminal state beyond the expected time window
- Rejected transition rate elevated (callers sending invalid events for the current state)
- Concurrent transition attempts detected on the same entity (race condition)
- Unexpected transition path appearing (source-event-target tuple not in the defined table)
- Guard condition failures spiking (data issues or misconfiguration)
