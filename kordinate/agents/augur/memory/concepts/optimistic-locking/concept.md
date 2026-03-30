---
description: Optimistic Locking architectural pattern
type: pattern
testable: true
graphable: true
abstraction: [data, concurrency]
---
# Optimistic Locking

## Recognition

How to identify this pattern in code.

### Signatures

- `version` column or field on database entities, incremented on each update
- `@Version` annotation (JPA/Hibernate), `lock_version` (Rails), `__v` (Mongoose)
- `ETag` response header paired with `If-Match` conditional request header
- `UPDATE ... WHERE version = ?` or `UPDATE ... WHERE updated_at = ?` conditional writes
- `StaleObjectError` (Rails), `OptimisticLockException` (JPA), `VersionError` exception handling
- CAS (compare-and-swap) operations in distributed stores (Redis `WATCH`/`MULTI`, DynamoDB conditional expressions)
- `ConditionalCheckFailedException` (DynamoDB), `cas` parameter in Consul/etcd

### Confidence

- **high** -- Version column with conditional `UPDATE ... WHERE version = ?` and explicit conflict exception handling
- **medium** -- ETag/If-Match headers on API endpoints or `@Version` annotation present on entities
- **low** -- Timestamp-based conflict detection (`updated_at` comparison) without explicit version tracking

## Architecture

Look for version-based conflict detection on writes with clear retry or conflict resolution strategy.

### Review Checklist

- Every mutable entity has a version field that is atomically incremented on update
- Write operations use conditional updates that fail if the version has changed since the read
- Conflict handling is explicit: retry with fresh data, merge, or surface the conflict to the user
- Read-modify-write cycles are as short as possible to minimize the conflict window
- API layer surfaces version information (ETag/If-Match) so clients can participate in conflict detection
- High-contention entities have been identified and optimistic locking is appropriate for their write frequency

### Anti-patterns

- Silently overwriting data on conflict (last-write-wins) without detecting the version mismatch
- Infinite retry loops on conflict without backoff or a maximum retry count
- Using optimistic locking on high-contention resources where most writes will conflict and retry
- Checking the version in application code instead of the database WHERE clause (race condition)
