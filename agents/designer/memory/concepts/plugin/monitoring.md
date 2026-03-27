---
description: Plugin Architecture — monitoring guidance
curated: true
scope: global
preloaded: none
---
## Monitoring

Track plugin lifecycle events and failure rates to catch misbehaving plugins before they affect the core.

### Key Metrics

- `plugin_registered_total` (counter) — plugin registrations at startup and runtime
- `plugin_active` (gauge) — currently active plugins by name and version
- `plugin_errors_total` (counter) — failures per plugin (init, execution, shutdown)
- `plugin_execution_duration_seconds` (histogram) — per-plugin invocation latency

### Alerts

- Plugin failing to register or initialize at startup
- Plugin error rate exceeding threshold (noisy or broken plugin)
- Plugin execution latency p99 degrading core response times
- Active plugin count dropping unexpectedly (plugin crash or deregistration)
