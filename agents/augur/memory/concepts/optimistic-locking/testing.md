---
description: Optimistic Locking — testing guidance
type: supplementary
---
## Testing

Test conflict detection, version increment correctness, and retry/resolution behavior on concurrent writes.

### Unit Tests

- Read an entity, modify it, save with the correct version, and verify the version increments
- Read an entity, simulate a concurrent update (increment version in DB), then attempt save and assert conflict error
- Verify ETag/If-Match round-trip: response ETag matches the version, conditional PUT with stale ETag returns 409
- Test retry logic: on conflict, verify the code re-reads fresh data and retries with the new version

### Concurrency Tests

- Launch parallel updates to the same entity and verify exactly one succeeds per version, others receive conflict errors
- Simulate high-contention updates and verify retry with backoff eventually converges without infinite loops
- Test that the retry count is bounded and a final failure is surfaced after max retries

### Integration Tests

- Verify the version column is atomically incremented in the database WHERE clause, not in application code
- Test across API boundaries: two clients read the same resource, both PUT with the original ETag, only the first succeeds
- Confirm conflict errors include enough information (current version, conflicting fields) for client-side resolution
