---
description: Hexagonal — monitoring guidance
---
## Monitoring

Track port and adapter health to catch infrastructure failures before they leak into the domain.

### Key Metrics

- `adapter_call_duration_seconds` (histogram) — latency per adapter, broken down by port
- `adapter_errors_total` (counter) — failures per adapter (connection errors, timeouts)
- `domain_call_total` (counter) — domain service invocations vs adapter invocations (ratio check)
- `adapter_health` (gauge) — availability state per adapter (1=healthy, 0=degraded)

### Alerts

- Adapter error rate exceeding threshold for any single port
- Domain-to-adapter call ratio inversion (infra calls dominating domain calls)
- Adapter latency p99 exceeding SLA for a sustained period
