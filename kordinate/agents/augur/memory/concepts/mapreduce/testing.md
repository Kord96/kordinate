---
description: MapReduce — testing guidance
type: supplementary
---
## Testing

Verify map and reduce function correctness independently, then test the full job on representative data.

### Unit Tests

- Test the map function with known inputs and assert the exact set of intermediate key-value pairs
- Test the reduce function with grouped intermediate values and assert the correct aggregated output
- Verify the reduce function is associative: `reduce(a, reduce(b, c)) == reduce(reduce(a, b), c)`

### Integration Tests

- Run the full job on a small, representative dataset and compare output against a golden reference
- Test with skewed data (one key having disproportionately many values) and verify correctness and completion
- Re-run the job on the same input and assert identical output (idempotency)

### Failure Injection

- Kill a mapper or reducer mid-task and verify the framework retries and completes the job correctly
- Introduce a poison record in the input and verify the job handles it gracefully (skip or dead-letter)
