---
description: WebSocket — deployment guidance
type: supplementary
---
## Deployment

Plan for mass reconnection storms during rollouts, since every terminated pod forces all its connected clients to reconnect simultaneously.

### Rollout Implications

- Terminating a pod kills all WebSocket connections on that pod at once — clients reconnect simultaneously, creating a thundering herd on the remaining pods
- Connection draining must allow existing WebSocket connections to close gracefully — unlike HTTP requests, WebSocket connections are long-lived and may be mid-stream when a pod is marked for termination
- Load balancer configuration must support WebSocket upgrade headers — a deploy that changes load balancer settings can silently break the HTTP-to-WebSocket upgrade handshake
- Rolling deployments cause clients to reconnect to new pods, potentially losing in-memory session state — any state tied to the connection (subscriptions, cursor position) must be recoverable on reconnect
- Message format changes must be backward-compatible because connected clients may be on older versions and do not redeploy on your schedule

### Pre-deploy Checklist

- Verify load balancer supports WebSocket upgrade headers and sticky sessions if required
- Configure terminationGracePeriodSeconds long enough for existing WebSocket connections to close gracefully
- Test client reconnection behavior during rolling deployments to ensure seamless recovery
- Confirm server-side connection limits and backpressure are configured before scaling up client-facing capacity
- Verify authentication during the upgrade handshake works correctly after any auth infrastructure changes
- Monitor connection counts during deployment to verify clients reconnect to new instances without pile-up
