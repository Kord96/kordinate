---
description: API Gateway — deployment guidance
---
## Deployment

Route changes and upstream health checks during rollout determine whether traffic reaches the correct backends.

### Rollout Implications

- Route configuration changes should deploy separately from backend service changes — avoid deploying both simultaneously
- During rolling updates of backend services, the gateway must detect unhealthy upstream pods and stop routing to them
- Rate limit and auth policy changes take effect immediately on reload — verify new limits do not inadvertently block legitimate traffic
- Gateway reload or restart drops in-flight connections — use graceful reload mechanisms that drain existing connections

### Pre-deploy Checklist

- Verify upstream backend services are healthy and have sufficient capacity before deploying gateway route changes
- Confirm rate limit and auth policy changes have been tested against expected traffic patterns
- Check that health check intervals and thresholds are tuned for the rollout speed (avoid marking healthy pods as down during restart)
