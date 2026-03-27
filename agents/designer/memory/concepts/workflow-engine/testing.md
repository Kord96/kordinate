---
description: Workflow Engine — testing guidance
type: supplementary
curated: true
scope: global
preloaded: none
---
# Testing

- Test that each step is idempotent: executing a step twice with the same input produces the same result
- Verify DAG validation: circular dependencies are detected and rejected at definition time
- Test workflow state persistence: crash and restart the engine, then verify workflows resume from the last checkpoint
- Test per-step retry and timeout policies independently from the workflow orchestration
- Verify that failed workflows can be retried from the point of failure, not only from the beginning
- Test conditional branching: workflows with if/else or switch steps follow the correct path
- Integration test the full workflow end-to-end with realistic step implementations
- Test composed sub-workflows to verify they integrate correctly into parent workflows
