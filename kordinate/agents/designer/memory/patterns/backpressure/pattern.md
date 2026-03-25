---
description: Backpressure architectural pattern
curated: true
scope: global
preloaded: none
---
# Backpressure

## Architecture

Flow control mechanism for when a producer is faster than its consumer. Prevents memory exhaustion and queue overflow by signaling the producer to slow down or by shedding load. Common strategies include rate limiting, bounded queues with rejection, and reactive pull-based consumption.

## Monitoring

Track producer-consumer imbalance and resource exhaustion signals.

### Key Metrics

- `queue_depth` (gauge) — pending items between producer and consumer
- `consumer_lag` (gauge) — how far behind the consumer is (Kafka offset lag)
- `memory_pressure_bytes` (gauge) — buffer memory usage approaching limits
- `dropped_messages_total` (counter) — messages shed under load

### Alerts

- Queue depth growing monotonically (consumer not keeping up)
- Consumer lag exceeding SLA threshold
- Memory usage approaching configured buffer limits
- Non-zero drop rate when drops are not expected

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

## Testing

Verify that flow control activates under load, sheds excess traffic predictably, and recovers when pressure subsides.

### Unit Tests

- Test flow control activation: when the queue reaches the configured high-water mark, assert the producer is signaled to slow down or requests are rejected
- Verify shedding behavior: under sustained overload, assert messages are dropped or rejected according to the configured policy (oldest-first, random, priority-based)
- Test recovery: after the queue drains below the low-water mark, assert the producer is unblocked and normal throughput resumes
- Assert bounded queue semantics: submitting beyond queue capacity returns a rejection rather than blocking indefinitely

### Integration Tests

- Run a producer faster than the consumer against real infrastructure and verify backpressure engages without OOM or data corruption
- Test end-to-end recovery: apply load until backpressure activates, reduce load, and verify the system returns to normal throughput and latency
- Verify that backpressure metrics (queue depth, drop count, consumer lag) accurately reflect the system state under load

### Failure Injection

- Kill the consumer entirely and verify the producer hits backpressure limits rather than filling memory unboundedly
- Simulate a consumer that alternates between fast and stalled processing — verify backpressure engages and disengages correctly
- Introduce network partition between producer and consumer and verify the bounded queue prevents resource exhaustion on the producer side
