---
description: Batch Loader (N+1 Prevention) — testing guidance
type: supplementary
curated: true
scope: global
preloaded: none
---
## Testing

Verify that individual loads are batched into a single query and results are correctly dispatched.

### Unit Tests

- Schedule multiple loads within the same tick and assert they consolidate into one batch call
- Verify each caller receives the correct result for its key from the batched response
- Test cache behavior: repeated loads for the same key return cached results without re-batching

### Integration Tests

- Wire the batch loader against a real data source and assert query count equals 1 for N requested keys
- Test across nested resolvers (e.g., GraphQL) and verify N+1 queries are eliminated

### Failure Injection

- Return a partial batch response (some keys missing) and verify callers for missing keys receive clear errors
