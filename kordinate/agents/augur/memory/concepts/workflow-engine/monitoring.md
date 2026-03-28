---
description: Workflow Engine — monitoring guidance
type: supplementary
curated: true
scope: global
preloaded: none
---
# Monitoring

- Track per-step execution duration and success/failure rates to identify bottleneck or failing steps
- Alert on workflows stuck in a non-terminal state beyond an expected time threshold
- Monitor retry rates per step — sustained retries indicate a non-transient failure
- Track active workflow count and alert on unexpected growth (runaway workflow creation)
- Monitor workflow state persistence health — store outage means lost progress on all active workflows
- Dashboard showing workflow completion rates, average duration, and step-level success heatmap
- Alert on circular dependency detection or invalid DAG definitions at definition time
