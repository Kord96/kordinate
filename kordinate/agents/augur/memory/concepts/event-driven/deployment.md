---
description: Event-Driven — deployment guidance
type: supplementary
curated: true
scope: global
preloaded: none
---
## Deployment

Coordinate producer and consumer deployments to avoid event loss or processing gaps during rollouts.

### Rollout Implications

- Deploy consumers before producers when introducing new event types — consumers must be ready to handle events as soon as they appear
- Rolling consumer updates may cause temporary rebalancing of partitions — expect brief processing pauses during rebalance
- Verify that new consumers can handle events published by the old producer version and vice versa
- If changing event routing (new topics, partition keys), deploy the infrastructure change before the code change

### Pre-deploy Checklist

- Confirm message broker topics/queues exist and have correct partition counts in the target environment
- Verify consumer group offsets are committed and current — stale offsets after deploy could trigger unwanted replay
