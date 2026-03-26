---
description: Idempotent Consumer architectural pattern
curated: true
scope: global
preloaded: none
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

### Anti-patterns

- In-memory-only deduplication sets that lose state on restart
- Check-then-act without atomicity (race condition between duplicate check and processing)
- Unbounded growth of the processed ID store with no expiry or compaction
- Treating duplicates as errors instead of silently returning the original result
