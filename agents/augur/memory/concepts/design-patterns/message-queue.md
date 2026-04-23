---
kind: concept
name: message-queue
signatures: {}
type: pattern
abstraction:
- messaging
- infrastructure
scope: cross-cutting
status: primary
family: design-patterns
---

# Explanation

## Recognition

How to identify this pattern in code.

### Signatures

- Point-to-point messaging: each message consumed by exactly one consumer
- Queue declarations with `queue_declare()`, `create_queue()`, or queue name configuration
- Acknowledgment/nack: `ack()`, `nack()`, `reject()`, visibility timeout
- Worker processes consuming from named queues
- Libraries: RabbitMQ, AWS SQS, Celery task queues, Bull/BullMQ, Sidekiq
- `@task` or `@job` decorators dispatching work to a queue
- Message serialization: JSON payloads, protobuf, or pickle

### Confidence

- **high** -- named queue with explicit produce/consume, ack/nack, and single-delivery semantics
- **medium** -- task decorator dispatching to a background worker framework
- **low** -- in-process job queue or thread pool with a task list

## Architecture

Look for point-to-point message delivery with explicit acknowledgment ensuring each message is processed once.

### Review Checklist

- Messages are acknowledged only after successful processing (not before)
- Failed messages are retried with backoff before being dead-lettered
- Message payload is self-contained (consumer does not need to fetch additional context)
- Queue depth is monitored and alerts fire on sustained growth
- Consumer idempotency handles redelivered messages after ack timeout
- Poison messages are detected and routed to a dead-letter queue

### Anti-patterns

- Acknowledging messages before processing completes (data loss on crash)
- Unbounded retries without a dead-letter destination (infinite retry loops)
- Large payloads in the message body instead of a reference to external storage
- No visibility timeout tuning, causing duplicate processing under load

### Relationship To Other Concepts

- Related to [dead-letter](/concepts/dead-letter) because queues often need a failure sink for poison or repeatedly failing messages.
- Related to [competing-consumers](/concepts/competing-consumers) when multiple workers share one queue and each message is processed by only one worker.
- Related to [claim-check](/concepts/claim-check) when large payloads are replaced by references to external storage.

### Boundary

Use `message-queue` when work or messages are decoupled through queued delivery with acknowledgment, redelivery, or visibility semantics.

Do not use it for pub-sub topics or in-process event emitters unless queue semantics are the core behavior.
