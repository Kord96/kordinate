---
description: Pipeline/Filter — testing guidance
type: supplementary
---
## Testing

Test each stage in isolation, then verify correct data flow and error propagation through the full pipeline.

### Unit Tests

- Test each filter/stage independently with known inputs and verify the output matches the expected transformation
- Verify stages conform to the uniform interface contract (same input/output shape or protocol)
- Pass edge-case inputs through individual stages: empty collections, null fields, maximum-size payloads
- Assert stages are pure (no hidden shared state) by running the same input twice and comparing outputs

### Pipeline Tests

- Compose the full pipeline and verify end-to-end output for a representative input
- Remove a stage from the pipeline and verify the remaining stages still function (no implicit coupling)
- Insert a new stage at different positions and verify it integrates without breaking adjacent stages
- Test error propagation: inject a failure in a mid-pipeline stage and verify it surfaces correctly (not swallowed)

### Performance Tests

- Measure throughput of the full pipeline and identify bottleneck stages
- Test with large inputs to verify no stage buffers the entire dataset in memory when streaming is expected
