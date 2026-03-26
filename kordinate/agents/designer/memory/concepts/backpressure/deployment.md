---
description: Backpressure — deployment guidance
curated: true
scope: global
preloaded: none
---
## Deployment

Buffer sizing and flow control threshold changes during rollout affect the producer-consumer balance.

### Rollout Implications

- Reducing buffer sizes during rollout causes earlier backpressure signals — producers may throttle or drop messages unexpectedly
- Scaling consumers down during rolling restart reduces throughput — producers must handle increased backpressure without data loss
- Flow control threshold changes take effect per-pod, so mixed old/new thresholds during rollout create uneven load distribution
- New pods starting with empty buffers temporarily absorb more load, potentially starving old pods that are draining

### Pre-deploy Checklist

- Verify buffer size changes are within safe bounds — too small causes premature drops, too large risks OOM
- Confirm consumer scaling strategy accounts for reduced capacity during rolling restart
- Check that producers handle backpressure signals gracefully (throttle or queue, not crash)
