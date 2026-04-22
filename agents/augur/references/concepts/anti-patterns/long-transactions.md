---
kind: concept
name: long-transactions
signatures: {}
source:
  memory_concept: memory/catalog/concepts/long-transactions.md
type: anti-pattern
abstraction: []
scope: cross-cutting
status: supporting
---

# Explanation

## Recognition

How to identify this anti-pattern in code.

### Signatures

- Database transaction wrapping HTTP calls or external API calls
- `BEGIN` with no matching `COMMIT` for extended periods (visible in `pg_stat_activity` or slow query logs)
- `@transaction.atomic` or `@Transactional` around slow operations (file I/O, network requests, queue publishing)
- Lock wait timeouts appearing in application logs
- Transaction isolation level set to SERIALIZABLE without justification
- Connection checkout duration metrics showing long hold times

### Confidence

- **high** -- a database transaction block contains an HTTP request, external API call, or `sleep()`, confirmed by lock wait timeouts or connection pool exhaustion in production
- **medium** -- `@transaction.atomic` or `with transaction:` wraps a block that includes non-database I/O such as file writes, message publishing, or email sending
- **low** -- transaction boundaries span an entire request handler rather than being scoped to the specific database operations that require atomicity

## Impact

Connection pool exhaustion, deadlocks, and blocked queries that cascade into application-wide slowdowns.

### Symptoms

- Database connection pool is frequently exhausted under moderate load
- Deadlock errors appear in application or database logs
- Other queries are blocked waiting for locks held by long-running transactions
- Application latency spikes correlate with external service slowdowns (because the transaction holds while waiting)
- `idle in transaction` connections accumulate in the database

### Remediation

- Move external calls (HTTP, message publishing, file I/O) outside the transaction boundary
- Scope transactions to the minimum set of database operations that require atomicity
- Use the outbox pattern for operations that need both a database write and a message publish
- Set statement and idle-in-transaction timeouts at the database level (`idle_in_transaction_session_timeout`)
- Monitor transaction duration and alert on transactions exceeding a threshold (e.g., 5 seconds)

### Relationship To Other Concepts

- Related to [unit-of-work](/concepts/unit-of-work) because poorly scoped units of work often lead to transactions held open too long.
- Related to [outbox](/concepts/outbox) because outbox is a common remedy for moving external publication out of the transaction boundary.
- Related to [distributed-lock](/concepts/distributed-lock) when long-running transactions and locks combine to amplify contention and failure impact.

### Boundary

Use `long-transactions` when transaction scope is held open long enough to increase lock contention, failure blast radius, or latency significantly.

Do not use it for any nontrivial transaction. The key issue is harmful duration, especially around waits or external calls.
