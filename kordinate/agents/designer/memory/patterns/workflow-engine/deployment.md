---
description: Workflow Engine — deployment guidance
type: supplementary
curated: true
scope: global
preloaded: none
---
# Deployment

- Deploy workflow definition changes with version compatibility — in-flight workflows must complete on the old definition
- Ensure workflow state persistence survives deployment restarts (no in-memory-only state)
- Deploy step retry and timeout policy changes independently from step logic changes
- Test that new workflow versions can coexist with old versions during rolling deployments
- Verify workflow engine health checks after deployment before routing new workflow submissions
- Coordinate step-level dependency changes (new external services) with infrastructure provisioning
- Monitor in-flight workflow completion rates during deployment to detect regressions early
