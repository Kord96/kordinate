---
description: Value Object — testing guidance
type: supplementary
curated: true
scope: global
preloaded: none
---
# Testing

- Test equality: two value objects with the same fields must be equal regardless of identity
- Test immutability: attempting to modify a field after construction must raise an error or be impossible
- Verify hash consistency: equal objects must produce the same hash (safe for use as dict keys / set members)
- Test validation at construction: invalid field combinations must be rejected at creation time
- Test transformation methods: they must return new instances, not modify the original
- Assert that value objects do not have an `id` field participating in equality checks
- Test serialization and deserialization roundtrips (JSON, pickle) to verify equality is preserved
- Test edge cases: boundary values, empty strings, zero amounts, negative values
