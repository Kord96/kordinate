---
description: GraphQL — testing guidance
type: supplementary
curated: true
scope: global
preloaded: none
---
## Testing

Test schema validity, resolver correctness, and query behavior including edge cases around nullability and errors.

### Unit Tests

- Test each resolver independently with mocked data sources and assert correct return shapes
- Verify nullable fields return null without causing resolver chain failures
- Test input validation: invalid arguments should produce structured GraphQL errors, not 500s
- Assert that resolvers do not over-fetch from data sources — verify only requested fields trigger backend calls

### Integration Tests

- Execute full queries against a running server and compare responses against expected JSON snapshots
- Test mutations end-to-end: mutate, then query the affected data and verify consistency
- Verify N+1 query prevention: use a data loader/batch loader and assert the number of backend calls is bounded
- Test subscription delivery: subscribe, trigger a mutation, and verify the subscriber receives the update

### Schema Tests

- Validate the schema against breaking change detection rules before merge (removed fields, type changes)
- Test that deprecated fields still resolve correctly and return deprecation warnings
