## Testing

Verify correct handoff between producers and consumers, bounded buffer behavior, and clean shutdown.

### Unit Tests

- Produce N items, consume N items, and verify all items are received in FIFO order
- Fill the queue to capacity and verify the producer blocks or receives a queue-full signal
- Consume from an empty queue and verify the consumer blocks or times out without error
- Send a poison pill or shutdown signal and verify the consumer exits its processing loop cleanly

### Concurrency Tests

- Run multiple producers and multiple consumers simultaneously and verify no item is processed twice or lost
- Verify no deadlock when producers and consumers contend on a full or empty queue
- Interrupt a consumer thread mid-processing and verify the item is not silently dropped

### Integration Tests

- Produce items faster than the consumer can process and verify backpressure engages (queue bounded, producer slows)
- Simulate a consumer crash and restart, then verify remaining items in the queue are eventually processed
- Verify error handling: a consumer that fails on one item continues processing subsequent items

## Monitoring

Track queue depth, throughput imbalance, and consumer health to detect backlog buildup early.

### Key Metrics

- `queue_depth` (gauge) -- current number of items in the shared buffer
- `queue_capacity_utilization` (gauge) -- queue depth as a percentage of max capacity
- `producer_enqueue_rate` (counter) -- items enqueued per second
- `consumer_dequeue_rate` (counter) -- items dequeued and processed per second
- `consumer_processing_errors_total` (counter) -- items that failed processing in the consumer

### Alerts

- Queue depth exceeds high-water mark (consumers falling behind producers)
- Queue at capacity for more than a sustained period (producers blocking or dropping)
- Consumer dequeue rate drops to zero while queue depth is nonzero (consumer stalled or dead)
- Consumer error rate exceeds threshold (poison messages or downstream failure)

