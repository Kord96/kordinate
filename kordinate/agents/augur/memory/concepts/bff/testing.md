---
description: Backend for Frontend — testing guidance
type: supplementary
---
## Testing

Test response aggregation, client-specific shaping, and graceful degradation when upstream services fail.

### Unit Tests

- Verify response shape matches the contract expected by the target client (web, mobile, etc.)
- Test aggregation logic: multiple upstream responses are merged into the correct BFF response
- Assert that unnecessary fields are stripped and client-specific transformations are applied

### Integration Tests

- Wire the BFF against stubbed upstream services and verify end-to-end response assembly
- Test with multiple BFF variants (web, mobile) against the same upstreams to verify different output shapes

### Failure Injection

- Take down one upstream and verify the BFF returns a partial response with degradation markers rather than a full failure
