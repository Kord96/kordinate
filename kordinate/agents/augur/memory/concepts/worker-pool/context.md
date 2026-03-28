# Testing

- Test that pool size is configurable and tasks execute concurrently up to the pool limit
- Verify graceful shutdown: pending tasks complete before the pool terminates
- Test exception handling in worker tasks — exceptions must be captured and reported, not silently lost
- Test task timeout enforcement: long-running tasks are terminated after the configured timeout
- Verify that submitted tasks are independent — no hidden shared mutable state between tasks
- Test queue depth limits: submitting beyond capacity rejects or blocks as configured
- Test that future/result objects are properly consumed and not leaked
- Load test the pool with burst submissions to verify backpressure and queue behavior

# Monitoring

- Track pool utilization: active workers vs pool size to detect saturation
- Alert when the task submission queue depth exceeds a threshold (backlog building up)
- Monitor per-task execution duration and alert on tasks exceeding the configured timeout
- Track task failure rates and exception types to detect systematic errors
- Alert on worker starvation: all workers busy with long-running tasks blocking new submissions
- Dashboard showing pool size, active workers, queue depth, and task completion rates over time
- Monitor for leaked futures: submitted tasks whose results are never consumed

