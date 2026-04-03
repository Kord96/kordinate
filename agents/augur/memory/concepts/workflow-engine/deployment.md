---
description: Workflow Engine — deployment guidance
type: supplementary
---
## Deployment

Deploy workflow definition changes with version isolation so that in-flight workflows complete on the definition they started with.

### Rollout Implications

- In-flight workflows must complete on the old definition — deploying a new workflow version that immediately applies to running executions can corrupt state or skip steps
- Rolling deployments create a window where old and new workflow engine pods coexist — both must be able to process the same workflow versions without conflicting on step execution or state transitions
- Workflow state must survive pod restarts — if state is held in memory, a rolling restart loses all progress for in-flight workflows, requiring full re-execution
- Deploying step retry or timeout policy changes affects currently-executing workflows — tightening a timeout may cause a step that was within limits on the old policy to fail immediately
- Adding a new external dependency to a workflow step requires that the dependency is provisioned and reachable before the workflow engine deploy — otherwise the step fails on first execution

### Pre-deploy Checklist

- Verify workflow state persistence survives deployment restarts (no in-memory-only state)
- Confirm new workflow versions can coexist with old versions and that in-flight executions are not interrupted
- Deploy step retry and timeout policy changes independently from step logic changes to isolate impact
- Ensure new external dependencies referenced by workflow steps are provisioned and reachable
- Monitor in-flight workflow completion rates during deployment to detect regressions early
