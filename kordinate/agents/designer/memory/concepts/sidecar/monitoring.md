---
description: Sidecar — monitoring guidance
curated: true
scope: global
preloaded: none
---
## Monitoring

Track sidecar health and resource consumption to ensure sidecars do not degrade the main container.

### Key Metrics

- `sidecar_health` (gauge) — health status per sidecar (1=healthy, 0=degraded)
- `sidecar_cpu_usage_ratio` (gauge) — sidecar CPU usage as fraction of pod CPU limit
- `sidecar_memory_usage_bytes` (gauge) — sidecar memory consumption
- `sidecar_request_duration_seconds` (histogram) — latency of requests proxied through the sidecar
- `sidecar_errors_total` (counter) — errors in sidecar-to-main or sidecar-to-external communication

### Alerts

- Sidecar consuming more than expected share of pod resources (resource budget breach)
- Sidecar health check failing while main container is healthy (lifecycle mismatch)
- Sidecar proxy latency adding unacceptable overhead to main container requests
- Sidecar restart count exceeding threshold (unstable sidecar affecting pod stability)
