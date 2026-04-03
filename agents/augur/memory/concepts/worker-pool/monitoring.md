---
description: Worker/Thread Pool — monitoring guidance
---
## Monitoring

Track pool utilization, queue depth, and per-task execution health to prevent saturation and detect failures.

### Key Metrics

- `pool_active_workers` (gauge) — workers currently executing tasks versus total pool size
- `pool_utilization_ratio` (gauge) — fraction of workers busy, indicates headroom or saturation
- `pool_queue_depth` (gauge) — tasks waiting in the submission queue for an available worker
- `pool_task_duration_seconds` (histogram) — per-task execution time, partitioned by task type
- `pool_task_failures_total` (counter) — task exceptions partitioned by error type
- `pool_submitted_tasks_total` (counter) — tasks submitted to the pool over time

### Alerts

- Queue depth exceeding threshold (backlog building, pool cannot keep up)
- All workers busy with long-running tasks (worker starvation, new submissions blocked)
- Task execution exceeding configured timeout (hung task consuming a worker)
- Task failure rate elevated for a specific task type (systematic error)
- Submitted tasks whose futures are never consumed (leaked futures, resource waste)
