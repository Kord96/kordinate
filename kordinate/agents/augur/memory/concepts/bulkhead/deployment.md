---
description: Bulkhead — deployment guidance
curated: true
scope: global
preloaded: none
---
## Deployment

Pool size changes and connection draining must be coordinated to avoid resource exhaustion during rollout.

### Rollout Implications

- Reducing pool sizes during rollout can cause immediate rejection spikes if in-flight requests exceed the new limit
- New pods starting with fresh pools must warm up connections — expect higher latency during the initial requests
- Rolling restart temporarily reduces total pool capacity across the fleet — size pools to handle full load with one fewer pod
- Connection draining must complete before pod termination — active connections in a pool that are forcibly closed cause client errors

### Pre-deploy Checklist

- Verify pool size changes are gradual (not halving capacity in one step) to avoid rejection spikes
- Confirm terminationGracePeriodSeconds allows full connection draining per pool
- Check that monitoring is in place for per-pool rejection rates during the rollout window
