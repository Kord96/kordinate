---
kind: concept
name: dead-letter
signatures: {}
source:
  memory_concept: memory/catalog/concepts/dead-letter.md
type: pattern
abstraction:
- messaging
- resilience
scope: cross-cutting
status: primary
---

# Explanation

## Recognition

How to identify this pattern in code.

### Signatures

- DLQ or DLX (dead-letter exchange) configuration on queues or topics
- Failed message routing: messages moved after max retry count exceeded
- Retry count tracking: `x-death` headers, `retry_count` field, `delivery_count`
- Max retry limits: `max_retries`, `maxReceiveCount`, `x-max-retries`
- Poison message handling: dedicated error queue, alert on DLQ depth
- RabbitMQ `x-dead-letter-exchange`, SQS `RedrivePolicy`, Kafka error topics
- DLQ consumer or dashboard for inspecting and replaying failed messages

### Confidence

- **high** -- explicit DLQ configuration with retry count tracking and max retry threshold
- **medium** -- error handling that moves failed messages to a separate queue but without formal DLQ naming
- **low** -- failed messages logged or stored in a database table for manual review

## Architecture

Look for a secondary destination that captures messages that cannot be processed after exhausting retries.

### Review Checklist

- Max retry count is configured and appropriate for the failure type
- DLQ messages retain the original payload and failure metadata (reason, timestamp, stack trace)
- Alerting fires when DLQ depth exceeds zero or a threshold
- A replay mechanism exists to reprocess DLQ messages after fixing the root cause
- DLQ is monitored separately from the main queue

### Anti-patterns

- No DLQ configured, causing poison messages to block the queue or retry forever
- DLQ messages silently accumulating with no alerting or review process
- Replaying DLQ messages without fixing the underlying cause (re-poisoning the queue)
- Losing original message metadata during dead-lettering (cannot diagnose failures)

### Relationship To Other Concepts

- Related to [retry](/concepts/retry) because messages typically reach a dead-letter queue only after retry policy is exhausted.
- Related to [claim-check](/concepts/claim-check) when large failed payloads are represented indirectly and still need durable error handling.
- Related to [competing-consumers](/concepts/competing-consumers) when worker fleets can poison shared queues and need a safe failure sink.

### Boundary

Use `dead-letter` when failed messages are intentionally moved aside after repeated failure so the main queue or stream can continue processing.

Do not use it for generic error logging or retry counters unless failed work is actually redirected into a separate failure channel or queue.
