---
description: Worker/Thread Pool — monitoring guidance
type: supplementary
curated: true
scope: global
preloaded: none
---
# Monitoring

- Track pool utilization: active workers vs pool size to detect saturation
- Alert when the task submission queue depth exceeds a threshold (backlog building up)
- Monitor per-task execution duration and alert on tasks exceeding the configured timeout
- Track task failure rates and exception types to detect systematic errors
- Alert on worker starvation: all workers busy with long-running tasks blocking new submissions
- Dashboard showing pool size, active workers, queue depth, and task completion rates over time
- Monitor for leaked futures: submitted tasks whose results are never consumed
