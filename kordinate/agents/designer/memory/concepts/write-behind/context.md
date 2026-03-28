# Testing

- Test that writes to cache are eventually flushed to the backing store within the configured delay
- Simulate cache crash before flush and verify the data durability guarantee (what is lost, what survives)
- Test write coalescing: multiple writes to the same key produce a single flush with last-write-wins or merge
- Verify flush failure retry with backoff and dead-letter handling for permanently failing writes
- Test write ordering preservation: verify the backing store reflects the correct final state
- Test cache warm-up on startup: verify data is loaded from backing store before accepting new writes
- Assert that the write-behind buffer is bounded — reject or backpressure when buffer is full
- Test consistency monitoring: verify drift detection between cache and backing store catches divergence

# Monitoring

- Track write-behind buffer depth and alert when approaching memory limits (unbounded growth risk)
- Monitor flush latency and success/failure rates — flush failures risk data loss
- Alert on cache-to-store drift: periodically compare cached state with backing store for consistency
- Track write coalescing ratio (writes received vs writes flushed) to measure batching effectiveness
- Monitor flush retry counts and dead-letter handling for persistently failing flushes
- Dashboard showing buffer depth, flush rate, coalescing ratio, and backing store write latency
- Alert on cache startup: verify warm-up from backing store completes before accepting writes

