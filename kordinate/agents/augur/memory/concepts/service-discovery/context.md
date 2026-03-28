# Testing

- Test registration and deregistration lifecycle: service starts, registers, shuts down, deregisters
- Simulate health check failures and verify the instance is removed from the registry within the TTL
- Test consumer behavior when the registry returns zero healthy instances (fallback or clear error)
- Verify stale registration cleanup by letting TTL expire without heartbeat renewal
- Test network partition scenarios: registry unreachable, verify consumers use cached endpoints
- Load test the registry with rapid registration/deregistration cycles to verify stability
- Test load balancing strategy by resolving endpoints repeatedly and checking distribution
- Verify that DNS-based discovery respects TTL expiry and does not cache stale addresses indefinitely

# Monitoring

- Track registry health: number of registered instances, registration/deregistration rates
- Alert on stale registrations — instances whose health check has not succeeded within the TTL window
- Monitor lookup latency from the consumer side (time to resolve a service endpoint)
- Alert when a service has zero healthy instances in the registry
- Track health check failure rates per service to detect degrading instances before they are removed
- Monitor DNS TTL cache hit rates if using DNS-based discovery
- Dashboard showing service instance counts over time to detect unexpected scaling or deregistration events

# Deployment

- Deploy new instances with health checks passing before registering them in the discovery service
- Deregister instances before draining connections during rolling updates — avoid traffic to terminating pods
- Verify that DNS TTLs are short enough for deployments to propagate within the expected rollout window
- Test that cached endpoint lists expire gracefully when the registry is temporarily unreachable
- Coordinate registry infrastructure upgrades separately from application deployments
- Ensure discovery fallback (cached endpoints) is tested during registry maintenance windows
- Validate that new service versions register under the same service name with correct metadata/tags

