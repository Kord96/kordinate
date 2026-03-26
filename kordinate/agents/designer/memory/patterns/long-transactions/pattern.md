---
description: Long Transactions anti-pattern
type: anti-pattern
curated: true
scope: global
preloaded: none
---
# Long Transactions

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
