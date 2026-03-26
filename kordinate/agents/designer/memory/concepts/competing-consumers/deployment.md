---
description: Competing Consumers — deployment guidance
type: supplementary
curated: true
scope: global
preloaded: none
---
## Deployment

Scale consumers independently of producers and ensure no messages are lost during rolling restarts.

### Rollout Implications

- During rolling restart, in-flight messages on terminating instances must be nacked or completed before shutdown
- Old and new consumer versions may process messages concurrently — ensure message format backward compatibility
- Scaling down reduces parallelism; verify remaining consumers can handle the full message rate

### Pre-deploy Checklist

- Verify consumer shutdown drains in-flight messages within terminationGracePeriodSeconds
- Confirm consumer group rebalancing completes without message loss
