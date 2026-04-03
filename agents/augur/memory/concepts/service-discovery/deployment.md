---
description: Service Discovery — deployment guidance
type: supplementary
---
## Deployment

Coordinate registry state with pod lifecycle to avoid routing traffic to instances that are not yet ready or already draining.

### Rollout Implications

- New pods must pass health checks before registering in the discovery service — premature registration sends traffic to instances that are not ready to serve
- Deregister instances before initiating connection draining during rolling updates — stale registry entries route traffic to terminating pods
- DNS-based discovery is subject to TTL caching — if TTLs are longer than the rollout window, clients may resolve to pods that no longer exist
- Rolling restarts temporarily reduce the number of healthy registered endpoints — consumers relying on cached endpoint lists may see a higher error rate during the window
- If the registry itself is temporarily unreachable during a deploy, clients fall back to cached endpoints which may include pods that have already been replaced

### Pre-deploy Checklist

- Verify DNS TTLs are short enough for endpoint changes to propagate within the rollout window
- Confirm that new service versions register under the same service name with correct metadata and tags
- Test that cached endpoint lists expire gracefully when the registry is unreachable
- Ensure registry infrastructure upgrades are scheduled separately from application deployments
