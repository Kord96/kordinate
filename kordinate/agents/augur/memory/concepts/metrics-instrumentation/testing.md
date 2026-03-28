---
description: Metrics Instrumentation — testing guidance
type: supplementary
curated: true
scope: global
preloaded: none
---
## Testing

Verify that metrics are emitted correctly, labels are bounded, and the scrape endpoint returns valid output.

### Unit Tests

- Trigger an operation and assert the corresponding counter increments by exactly one
- Record a known duration and verify the histogram observation falls in the expected bucket
- Verify metric names follow the naming convention: `<namespace>_<subsystem>_<name>_<unit>`

### Integration Tests

- Scrape the `/metrics` endpoint and parse the output as valid Prometheus exposition format
- Exercise all instrumented code paths and verify every declared metric appears in the scrape output
- Assert that label cardinality is bounded: no user IDs, request IDs, or unbounded strings as label values

### Regression Tests

- Add a test that fails if a new metric is added without documentation or if naming conventions are violated
- Verify that no metrics are created inside request handlers (all should be registered at startup)
