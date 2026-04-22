---
kind: concept
name: batch-loader
signatures: {}
source:
  memory_concept: memory/catalog/concepts/batch-loader.md
type: pattern
abstraction:
- data
scope: domain
status: primary
---

# Explanation

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

### Relationship To Other Concepts

- Related to [n-plus-one](/concepts/n-plus-one) as the main remediation pattern for repeated per-item fetches.
- Related to [graphql](/concepts/graphql) because batch loaders are especially common inside resolver graphs where nested fetches would otherwise explode query counts.
- Related to [cache-aside](/concepts/cache-aside) when per-request batching also memoizes or deduplicates repeated reads.

### Boundary

Use `batch-loader` when many individual lookups are intentionally collapsed into one batched fetch with key-to-result remapping.

Do not use it for any bulk query. The important signal is demand-driven batching specifically to avoid repeated N+1-style access.
