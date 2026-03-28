---
description: Service Discovery — monitoring guidance
type: supplementary
curated: true
scope: global
preloaded: none
---
# Monitoring

- Track registry health: number of registered instances, registration/deregistration rates
- Alert on stale registrations — instances whose health check has not succeeded within the TTL window
- Monitor lookup latency from the consumer side (time to resolve a service endpoint)
- Alert when a service has zero healthy instances in the registry
- Track health check failure rates per service to detect degrading instances before they are removed
- Monitor DNS TTL cache hit rates if using DNS-based discovery
- Dashboard showing service instance counts over time to detect unexpected scaling or deregistration events
