---
kind: concept
name: competing-consumers
signatures: {}
source:
  memory_concept: memory/catalog/concepts/competing-consumers.md
type: pattern
abstraction:
- messaging
- concurrency
scope: cross-cutting
status: primary
---

# Explanation

## Recognition

How to identify this pattern in code.

### Signatures

- Multiple consumers reading from the same queue or topic partition
- Consumer groups: Kafka `group.id`, RabbitMQ multiple consumers on one queue
- Partition assignment and rebalancing logic
- Load balancing across consumers: round-robin, least-connections, or partition-based
- Concurrency configuration: `concurrency=N`, `prefetch_count`, `maxConcurrentConsumers`
- SQS with multiple readers, Celery worker pool, Sidekiq processes
- Auto-scaling consumer count based on queue depth

### Confidence

- **high** -- consumer group configuration with partition assignment and rebalance handling
- **medium** -- multiple worker processes or threads consuming from the same queue
- **low** -- horizontally scaled service instances that each poll the same data source

## Architecture

Look for multiple consumer instances sharing the workload of a single queue or topic, with each message processed by exactly one consumer.

### Review Checklist

- Message processing is idempotent (rebalancing may cause redelivery)
- Consumer rebalancing is handled gracefully (in-progress work is not lost)
- Prefetch/batch size is tuned to balance throughput and fairness
- Partition count or queue configuration supports the desired parallelism
- Consumer lag is monitored per consumer group
- Ordering guarantees are maintained within partitions where required

### Anti-patterns

- Assuming strict ordering across all messages when consumers process in parallel
- No rebalance listener, causing duplicate processing during consumer group changes
- All consumers configured with the same partition affinity (no actual distribution)
- Scaling consumers beyond the partition count (idle consumers with no work)

### Relationship To Other Concepts

- Related to [outbox](/concepts/outbox) when multiple workers or consumers drain staged work items or event rows for publication.
- Related to [dead-letter](/concepts/dead-letter) when poisoned work items must be removed from a shared consumer stream safely.
- Related to [worker-pool](/concepts/worker-pool) because both scale processing with multiple workers, though competing consumers coordinate over a shared message source.

### Boundary

Use `competing-consumers` when multiple consumers pull from the same queue or stream partition set and each work item is processed by only one of them.

Do not use it for pub-sub fan-out or generic worker pools unless the defining semantic is shared-consumption competition.
