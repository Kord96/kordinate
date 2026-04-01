---
description: Service Manager — deployment guidance
---
## Deployment

Graceful shutdown, health check timing, and startup dependencies determine whether rollouts cause traffic drops.

### Rollout Implications

- New pods must pass readiness probes before old pods begin terminating — configure minReadySeconds to avoid premature traffic shifting
- Startup dependencies (database, cache, message broker) must be reachable before readiness is signaled — use init containers or startup probes
- SIGTERM handling must drain in-flight requests and flush buffers within terminationGracePeriodSeconds or data is lost
- Health check timing mismatches between the orchestrator and the service can cause premature removal from load balancing

### Pre-deploy Checklist

- Verify terminationGracePeriodSeconds exceeds the maximum expected request drain time
- Confirm readiness and liveness probe intervals are tuned to avoid false positives during startup
- Check that all startup dependencies are available in the target environment before beginning rollout
