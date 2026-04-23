---
kind: concept
name: dual-writes
signatures: {}
type: anti-pattern
abstraction: []
scope: cross-cutting
status: supporting
family: anti-patterns
---

# Explanation

## Recognition

How to identify this anti-pattern in code.

### Signatures

- Writing to a database AND publishing to a message broker in the same method without a transactional outbox
- Separate try/catch blocks for database write and event publish
- `db.save()` followed by `producer.send()` or `queue.publish()` in sequence
- Cache write and database write in the same function without atomicity guarantees
- Writing to two different databases in a single operation without distributed transactions
- `commit()` followed by `notify()` or `emit()` where either can fail independently
- REST API call to another service after a local database write, with no compensation logic

### Confidence

- **high** -- database write and message broker publish in the same method, with separate error handling and no outbox pattern
- **medium** -- two different data stores written in sequence, where failure of the second leaves the first inconsistent
- **low** -- cache update and database write in the same path, but eventual consistency may be acceptable

## Impact

Data inconsistency between stores when either write fails, leaving the system in a partially updated state that is difficult to detect and repair.

### Symptoms

- Events published for records that were not persisted (or vice versa)
- Consumers process events for data that does not exist in the database
- Retry logic causes duplicate events or duplicate database entries
- Inconsistency reports between the database and downstream systems
- Manual reconciliation scripts needed to fix data drift between stores

### Remediation

- Implement the transactional outbox pattern: write the event to an outbox table in the same database transaction, then relay asynchronously
- Use change data capture (Debezium, DynamoDB Streams) to derive events from database changes
- If using Kafka, consider the Kafka transaction API for exactly-once semantics
- Replace dual writes with an event-sourced approach where the event log is the source of truth
- Add idempotency keys to consumers so that retries and duplicates are safe

See also: outbox pattern, change-data-capture pattern

### Relationship To Other Concepts

- Related to [outbox](/concepts/outbox) because outbox is one of the main remedies for avoiding inconsistent dual-write failure modes.
- Related to [change-data-capture](/concepts/change-data-capture) because CDC is another way to avoid publishing one change separately from the source-of-truth write.

### Boundary

Use `dual-writes` when one logical change is written to two systems separately without one durable coordination mechanism, creating inconsistency risk.

Do not use it for any system that touches multiple stores. The key signal is a fragile split write path with no reliable atomicity or recovery strategy.
