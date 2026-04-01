---
description: Service Manager — monitoring guidance
---
## Monitoring

Track service lifecycle transitions and health check outcomes to detect unstable services before they impact availability.

### Key Metrics

- `service_state` (gauge) — current lifecycle state per service (0=stopped, 1=starting, 2=ready, 3=draining)
- `service_restarts_total` (counter) — restart count per service (including crash restarts)
- `health_check_duration_seconds` (histogram) — health check execution time per service
- `health_check_failures_total` (counter) — failed health checks per service and probe type (liveness/readiness)

### Alerts

- Service restart count exceeding threshold in a rolling window (crash loop)
- Health check failing consecutively beyond configured threshold
- Service stuck in starting state beyond expected startup time
- Readiness probe failing while liveness passes (service alive but not serving)
