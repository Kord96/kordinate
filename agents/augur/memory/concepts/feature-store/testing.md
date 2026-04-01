---
description: Feature Store — testing guidance
type: supplementary
---
## Testing

Verify feature pipelines produce correct values and that online/offline serving returns consistent results.

### Unit Tests

- Test each feature transformation function with known inputs and assert exact expected outputs
- Verify null handling: missing source data should produce documented default values, not propagate nulls silently
- Assert that feature types match the declared schema (float, int, string, embedding) after transformation
- Test time-window aggregations with edge cases: empty windows, single-element windows, windows spanning DST changes

### Integration Tests

- Run the full feature pipeline on a sample dataset and compare output against a golden reference
- Fetch the same entity's features from both the online and offline store and verify consistency within the expected staleness window
- Test point-in-time correctness: features retrieved for a historical timestamp should reflect only data available at that time

### Online/Offline Parity

- Compare model predictions using online-served features vs offline-computed features for the same input set — divergence indicates a training-serving skew
