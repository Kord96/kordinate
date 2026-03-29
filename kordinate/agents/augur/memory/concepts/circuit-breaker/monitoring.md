---
description: Circuit Breaker — monitoring guidance
---
## Monitoring

Track circuit state transitions and dependency failure rates.

### Key Metrics

- `circuit_state` (gauge) — current state per dependency (0=closed, 1=open, 2=half-open)
- `circuit_failures_total` (counter) — failure count that drives the breaker
- `circuit_open_duration_seconds` (histogram) — how long circuits stay open before recovery
- `circuit_recovery_success_total` (counter) — successful half-open probes

### Alerts

- Circuit open for longer than expected recovery window
- High failure rate approaching breaker threshold (early warning)
- Repeated open-close cycling (flapping dependency)
