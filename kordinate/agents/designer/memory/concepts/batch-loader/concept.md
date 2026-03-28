---
description: Batch Loader (N+1 Prevention) architectural pattern
type: pattern
testable: true
curated: true
scope: global
preloaded: none
graphable: true
abstraction: [data]
---
# Batch Loader (N+1 Prevention)

## Recognition

How to identify this pattern in code.

### Signatures

- DataLoader pattern: batched key collection with deferred resolution (`new DataLoader(batchFn)`)
- Batched queries: `SELECT ... WHERE id IN (...)` replacing per-item lookups
- `prefetch_related` (Django), `includes` (Rails), `Include` (EF Core) for eager loading associations
- GraphQL DataLoader for batching field resolvers across a single request
- `@BatchMapping` (Spring), `@ResolveField` with loader injection
- Deferred resolution or promise-based batching that collects keys and flushes in one query
- Query batching middleware that groups individual lookups into bulk fetches

### Confidence

- **high** -- Explicit DataLoader instances or batch functions that collect keys and execute `WHERE id IN (?)`
- **medium** -- ORM eager loading directives (`includes`, `prefetch_related`) applied to associations
- **low** -- Manual query grouping where related IDs are collected into an array before a single query

## Architecture

Look for systematic batching of data fetches to eliminate per-item queries, especially in nested or graph-shaped data.

### Review Checklist

- DataLoader or equivalent batching is applied to all association lookups in resolver/handler layers
- Batch functions handle partial results gracefully (return null for missing keys, maintain key order)
- Cache scope is per-request to avoid serving stale data across different users or contexts
- Maximum batch size is configured to prevent excessively large `IN (...)` clauses
- Batch loaders are tested for correctness: key ordering matches result ordering
- N+1 detection tooling or query logging is in place to catch regressions

### Anti-patterns

- DataLoader cache persisting across requests, serving stale or leaked data between users
- Batch function that does not preserve key-to-result ordering, returning mismatched data
- Applying batching only at the top level while nested resolvers still trigger per-item queries
- No maximum batch size, generating SQL queries with thousands of IDs in the IN clause

See also: n-plus-one anti-pattern
