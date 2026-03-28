---
description: Inbox architectural pattern
curated: true
scope: global
preloaded: none
graphable: true
abstraction: [messaging, data, resilience]
---
# Inbox

## Recognition

How to identify this pattern in code.

### Signatures

- Database table named `inbox`, `processed_messages`, or `received_events`
- `message_id` column with a uniqueness constraint used for deduplication
- Check-before-process logic: query for existing `message_id` before handling the message
- `INSERT ... ON CONFLICT DO NOTHING` or equivalent upsert for idempotent message recording
- Consumer that writes the message ID to the inbox table in the same transaction as the business logic
- At-least-once delivery semantics from the message broker (Kafka, RabbitMQ, SQS)

### Confidence

- **high** -- Dedicated inbox table with `message_id` uniqueness constraint, dedup check before processing, and processing within a single transaction
- **medium** -- Message ID tracked in a general-purpose table or cache for deduplication, but not in the same transaction as business logic
- **low** -- Consumer code that checks "have I seen this before" using in-memory state or a cache with TTL

## Architecture

Look for idempotent message processing using a persistent deduplication table keyed on message ID.

### Review Checklist

- Message ID uniqueness is enforced at the database level (unique constraint or index)
- Dedup check and business logic execute in the same database transaction
- Inbox records are retained long enough to cover the broker's redelivery window
- Old inbox entries are periodically cleaned up to prevent unbounded table growth
- Processing failures do not insert into the inbox (message can be retried)

### Anti-patterns

- Deduplication based on in-memory sets or caches that lose state on restart
- Inbox insert committed before business logic completes (message marked as processed but work not done)
- No TTL or cleanup -- inbox table grows indefinitely
- Relying solely on the broker's exactly-once semantics instead of application-level idempotency
