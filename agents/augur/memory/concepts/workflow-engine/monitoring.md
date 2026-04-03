---
description: Workflow Engine — monitoring guidance
---
## Monitoring

Track workflow progression, per-step reliability, and engine health to detect stuck or failing workflows.

### Key Metrics

- `workflow_step_duration_seconds` (histogram) — execution time per workflow step, identifies bottlenecks
- `workflow_step_results_total` (counter) — step completions partitioned by step name and result (success, failure, timeout)
- `workflow_active_count` (gauge) — number of workflows currently in progress
- `workflow_stuck_count` (gauge) — workflows in a non-terminal state beyond the expected time threshold
- `workflow_step_retries_total` (counter) — retry attempts per step, sustained retries indicate non-transient failure
- `workflow_completion_duration_seconds` (histogram) — end-to-end workflow duration from start to terminal state

### Alerts

- Workflow stuck in a non-terminal state beyond the expected time threshold
- Step retry rate sustained (non-transient failure requiring investigation)
- Active workflow count growing unexpectedly (runaway workflow creation)
- Workflow state persistence store unhealthy (risks losing progress on all active workflows)
- Invalid DAG definition or circular dependency detected at definition time
