---
description: Message Queue — deployment guidance
type: supplementary
curated: true
scope: global
preloaded: none
---
## Deployment

Coordinate consumer rollouts with message processing to avoid message loss or duplicate processing.

### Rollout Implications

- Drain in-flight messages before terminating consumer pods (graceful shutdown with ack completion)
- During rolling updates, old and new consumer versions process from the same queue -- message format must be backward-compatible
- Scale consumers based on queue depth, but avoid scaling to zero if message loss is unacceptable
- Dead-letter queue configuration must exist before deploying consumers that rely on it

### Pre-deploy Checklist

- Verify queue and dead-letter queue exist in the target environment before deploying producers or consumers
- Confirm visibility timeout is tuned for the expected processing duration of the new consumer version
- Test that the new consumer version handles messages produced by the old producer version (schema compatibility)
- Ensure consumer graceful shutdown completes pending acks within `terminationGracePeriodSeconds`
