---
description: Service Discovery — testing guidance
type: supplementary
---
# Testing

- Test registration and deregistration lifecycle: service starts, registers, shuts down, deregisters
- Simulate health check failures and verify the instance is removed from the registry within the TTL
- Test consumer behavior when the registry returns zero healthy instances (fallback or clear error)
- Verify stale registration cleanup by letting TTL expire without heartbeat renewal
- Test network partition scenarios: registry unreachable, verify consumers use cached endpoints
- Load test the registry with rapid registration/deregistration cycles to verify stability
- Test load balancing strategy by resolving endpoints repeatedly and checking distribution
- Verify that DNS-based discovery respects TTL expiry and does not cache stale addresses indefinitely
