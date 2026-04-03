---
description: Service Discovery — monitoring guidance
---
## Monitoring

Track registry health, instance availability, and lookup performance across the discovery infrastructure.

### Key Metrics

- `discovery_registered_instances` (gauge) — number of registered instances per service
- `discovery_registration_events_total` (counter) — registrations and deregistrations over time
- `discovery_lookup_latency_seconds` (histogram) — time to resolve a service endpoint from the consumer side
- `discovery_health_check_failures_total` (counter) — failed health checks per service instance
- `discovery_stale_registrations` (gauge) — instances whose health check has not succeeded within the TTL window
- `discovery_dns_cache_hit_ratio` (gauge) — cache effectiveness for DNS-based discovery lookups

### Alerts

- Service has zero healthy instances in the registry (complete outage for that service)
- Stale registrations detected beyond the configured TTL (zombie instances receiving traffic)
- Health check failure rate rising for a service (degrading instances not yet removed)
- Lookup latency exceeding acceptable threshold (slows every service-to-service call)
- Unexpected drop in registered instance count (scaling event or mass deregistration)
