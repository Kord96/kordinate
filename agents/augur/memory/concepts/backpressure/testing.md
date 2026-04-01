---
description: Backpressure — testing guidance
---
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
