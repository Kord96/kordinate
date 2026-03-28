---
description: Stream-to-Store — deployment guidance
curated: true
scope: global
preloaded: none
---
## Deployment

Consumer rebalancing and offset management during rollout can cause duplicates or data loss if not handled correctly.

### Rollout Implications

- Rolling restart triggers consumer group rebalancing — ensure cooperative rebalancing is configured to minimize partition reassignment storms
- In-flight buffers must be flushed and offsets committed before a pod terminates, or data in the buffer is lost
- PVC-backed buffers require volume binding to complete before the consumer starts — account for this in readiness probes
- Scaling consumer replicas changes partition assignments — verify no partition is left unassigned during the transition
- New consumer instances starting with `latest` offset after a rebalance will skip unprocessed messages — always resume from committed offsets

### Pre-deploy Checklist

- Verify terminationGracePeriodSeconds is long enough to flush buffers and commit offsets
- Confirm PVCs are pre-provisioned or dynamic provisioning is fast enough to avoid readiness timeouts
- Check that consumer group rebalancing strategy is set to cooperative (incremental), not eager
