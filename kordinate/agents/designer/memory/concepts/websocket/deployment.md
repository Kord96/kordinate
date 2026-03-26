---
description: WebSocket — deployment guidance
type: supplementary
curated: true
scope: global
preloaded: none
---
# Deployment

- Deploy with connection draining: allow existing WebSocket connections to close gracefully before terminating pods
- Verify load balancer configuration supports WebSocket upgrade headers and sticky sessions if needed
- Deploy message format changes with backward compatibility — clients may be on older versions
- Test reconnection behavior during rolling deployments to ensure clients reconnect seamlessly
- Configure server connection limits and backpressure before scaling up client-facing capacity
- Verify authentication during the upgrade handshake works correctly after auth infrastructure changes
- Monitor connection counts during deployment to verify clients reconnect to new instances
