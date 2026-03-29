---
description: Bloom Filter — testing guidance
type: supplementary
---
## Testing

Verify zero false negatives, acceptable false positive rates, and correct sizing behavior.

### Unit Tests

- Insert known elements and assert membership queries return true for all (no false negatives)
- Query elements never inserted and verify the false positive rate stays within configured bounds
- Test filter capacity: after inserting the expected number of elements, assert error rate matches design

### Integration Tests

- Use the bloom filter as a cache guard: verify cache lookups are skipped for definitely-absent keys
- Test serialization and deserialization of the filter for persistence or transfer

### Failure Injection

- Overfill the filter beyond designed capacity and measure false positive rate degradation
