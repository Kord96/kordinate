---
description: Service Discovery — deployment guidance
type: supplementary
curated: true
scope: global
preloaded: none
---
# Deployment

- Deploy new instances with health checks passing before registering them in the discovery service
- Deregister instances before draining connections during rolling updates — avoid traffic to terminating pods
- Verify that DNS TTLs are short enough for deployments to propagate within the expected rollout window
- Test that cached endpoint lists expire gracefully when the registry is temporarily unreachable
- Coordinate registry infrastructure upgrades separately from application deployments
- Ensure discovery fallback (cached endpoints) is tested during registry maintenance windows
- Validate that new service versions register under the same service name with correct metadata/tags
