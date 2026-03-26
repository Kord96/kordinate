---
description: Idempotent Consumer architectural pattern
type: pattern
testable: true
observable: true
distributed: true
curated: true
scope: global
preloaded: none
graphable: true
---
# Idempotent Consumer

## Recognition

How to identify this pattern in code.

### Signatures

- Message ID deduplication before processing
- `processed_ids` set or table tracking already-handled messages
- Check-before-process pattern (lookup then conditionally execute)
- Idempotency keys in HTTP APIs
- `Idempotency-Key` header in request/response handling
- Upsert (`INSERT ... ON CONFLICT`) instead of plain insert
- Deduplication stores with TTL expiry
- Database table named `inbox`, `processed_messages`, or `received_events`
- `message_id` column with a uniqueness constraint used for deduplication
- `INSERT ... ON CONFLICT DO NOTHING` for idempotent message recording in an inbox table
- Consumer that writes the message ID to the inbox table in the same transaction as the business logic

### Confidence

- **high** -- `processed_ids` table/set combined with message ID lookup before processing, or `Idempotency-Key` header handling with stored results
- **medium** -- Upsert patterns in message handlers, or conditional inserts gated on existence checks
- **low** -- Generic duplicate checks without explicit idempotency infrastructure

## Architecture

Look for message deduplication at the consumer boundary with persistent tracking of processed IDs.

### Review Checklist

- Deduplication store is durable (survives restarts) and not just in-memory
- TTL or cleanup strategy exists to prevent unbounded growth of processed ID sets
- Idempotency check and processing happen atomically or within the same transaction
- Duplicate detection returns the original result, not an error
- Late or redelivered messages are handled gracefully (no side-effect replay)

### Database-Backed Variant (Inbox Table)

In the inbox variant, a dedicated database table (`inbox`, `processed_messages`, or `received_events`) provides the deduplication store. A `message_id` column with a uniqueness constraint enforces dedup at the database level. The consumer writes the message ID to the inbox table in the same transaction as the business logic, guaranteeing atomicity. This pairs with at-least-once delivery semantics from the message broker (Kafka, RabbitMQ, SQS).

Key review points for the inbox variant:
- Message ID uniqueness is enforced at the database level (unique constraint or index)
- Dedup check and business logic execute in the same database transaction
- Inbox records are retained long enough to cover the broker's redelivery window
- Old inbox entries are periodically cleaned up to prevent unbounded table growth
- Processing failures do not insert into the inbox (message can be retried)

### Anti-patterns

- In-memory-only deduplication sets that lose state on restart
- Check-then-act without atomicity (race condition between duplicate check and processing)
- Unbounded growth of the processed ID store with no expiry or compaction
- Treating duplicates as errors instead of silently returning the original result
- Inbox insert committed before business logic completes (message marked as processed but work not done)
- Relying solely on the broker's exactly-once semantics instead of application-level idempotency
