---
kind: concept
name: at-least-once-delivery
signatures: {}
type: pattern
abstraction:
- messaging
- resilience
scope: cross-cutting
status: primary
family: design-patterns
---

# Explanation

## Recognition

How to identify this pattern in code.

### Signatures

- Broker or transport may redeliver messages when acknowledgement is delayed or lost
- Consumer idempotency, deduplication tables, or replay-safe handlers are explicit requirements
- Visibility timeouts, ack/nack, retry queues, or redelivery policies shape design
- Documentation or code assumes duplicates are possible and must be tolerated

### Confidence

- **high** -- messaging or trigger path explicitly tolerates duplicates and relies on consumer-side idempotency
- **medium** -- retry and redelivery behavior exists, but duplicate-safety is only partially explicit
- **low** -- infrastructure likely redelivers under failure, but code treats delivery semantics implicitly

## Architecture

Look for systems where durability and retry matter more than duplicate suppression at the transport layer.

### Review Checklist

- Duplicate handling is explicit at the consumer boundary
- Message IDs or idempotency keys survive restarts
- Retry, redelivery, and poison-message handling are defined
- Product semantics tolerate repeated delivery attempts

### Anti-patterns

- Assuming one-and-only-one processing without deduplication
- Retrying side effects that are not idempotent
- No observability into redelivery volume or duplicate suppression

### Relationship To Other Concepts

- Related to [idempotent-consumer](/concepts/idempotent-consumer) because consumer-side duplicate safety is the standard response to at-least-once delivery.
- Related to [message-queue](/concepts/message-queue) when queue semantics and acknowledgement policies drive redelivery behavior.
- Related to [exactly-once-semantics](/concepts/exactly-once-semantics) as a stricter and harder alternative often approximated rather than truly achieved.

### Boundary

Use `at-least-once-delivery` when the architecture explicitly accepts redelivery and relies on duplicate-safe consumers.

Do not use it for any retry loop. The key signal is transport-level duplicate possibility.
