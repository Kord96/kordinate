# Testing

- Test that each step is idempotent: executing a step twice with the same input produces the same result
- Verify DAG validation: circular dependencies are detected and rejected at definition time
- Test workflow state persistence: crash and restart the engine, then verify workflows resume from the last checkpoint
- Test per-step retry and timeout policies independently from the workflow orchestration
- Verify that failed workflows can be retried from the point of failure, not only from the beginning
- Test conditional branching: workflows with if/else or switch steps follow the correct path
- Integration test the full workflow end-to-end with realistic step implementations
- Test composed sub-workflows to verify they integrate correctly into parent workflows

# Monitoring

- Track per-step execution duration and success/failure rates to identify bottleneck or failing steps
- Alert on workflows stuck in a non-terminal state beyond an expected time threshold
- Monitor retry rates per step — sustained retries indicate a non-transient failure
- Track active workflow count and alert on unexpected growth (runaway workflow creation)
- Monitor workflow state persistence health — store outage means lost progress on all active workflows
- Dashboard showing workflow completion rates, average duration, and step-level success heatmap
- Alert on circular dependency detection or invalid DAG definitions at definition time

# Deployment

- Deploy workflow definition changes with version compatibility — in-flight workflows must complete on the old definition
- Ensure workflow state persistence survives deployment restarts (no in-memory-only state)
- Deploy step retry and timeout policy changes independently from step logic changes
- Test that new workflow versions can coexist with old versions during rolling deployments
- Verify workflow engine health checks after deployment before routing new workflow submissions
- Coordinate step-level dependency changes (new external services) with infrastructure provisioning
- Monitor in-flight workflow completion rates during deployment to detect regressions early

