---
kind: concept
name: n-plus-one
signatures: {}
source:
  memory_concept: memory/catalog/concepts/n-plus-one.md
type: anti-pattern
abstraction: []
scope: cross-cutting
status: supporting
---

# Explanation

## Recognition

How to identify this anti-pattern in code.

### Signatures

- Database query inside a loop (`for item in items: item.related.load()`)
- Missing `prefetch_related`/`includes`/`JOIN` on ORM queries that access related objects
- ORM lazy loading triggered during iteration over a collection
- SQL log showing repeated identical queries with different IDs
- Data access layer returning parent objects without eagerly loading children that callers always need

### Confidence

- **high** -- SQL logs show N identical SELECT statements differing only by a foreign key value within a single request
- **medium** -- loop body accesses a relationship attribute on an ORM model without a prior prefetch or join
- **low** -- ORM query fetches a list without `select_related`/`includes` and the result is passed to a template or serializer

## Impact

Linear query explosion that overwhelms the database as dataset size grows.

### Symptoms

- Request latency scales linearly with the number of records
- Database CPU and connection count spike under normal load
- Slow query logs fill with trivially simple SELECTs
- Application appears fast in development (small dataset) but crawls in production
- Database connection pool exhaustion under moderate concurrency

### Remediation

- Use eager loading (`prefetch_related`, `includes`, `joinedload`) on all queries where related data will be accessed
- Batch-fetch related records in a single query using `WHERE id IN (...)` instead of looping
- Add a query counter in tests that asserts a maximum number of queries per endpoint
- Introduce a data loader or batch loader pattern for GraphQL or similar aggregation layers
- Profile with query logging enabled in staging to catch regressions before production

See also: batch-loader pattern (remediation)

### Relationship To Other Concepts

- Related to [batch-loader](/concepts/batch-loader) because this concept commonly appears alongside it or is clarified by contrast with it.

### Boundary

Use `n-plus-one` when the important observation is this specific recurring architectural failure mode within a cross-cutting architectural concern that can span multiple layers or services.

Do not use it just because a few signatures match; the surrounding responsibilities and architectural role should line up too.
