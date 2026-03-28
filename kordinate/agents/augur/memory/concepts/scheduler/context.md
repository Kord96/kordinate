# Testing

- Unit test job logic independently from the scheduler — inject a fake clock and trigger manually
- Test overlap protection by simulating a long-running job and verifying the next trigger is skipped or queued
- Test retry behavior by injecting failures and asserting retry count, backoff intervals, and dead-letter handling
- Verify graceful shutdown waits for in-progress jobs before terminating
- Test timezone handling with explicit timezone fixtures — daylight saving transitions cause real bugs
- Test cron expression parsing against known edge cases (leap years, month boundaries, `*/5` vs `5`)
- Integration test the full schedule-to-execution path with an accelerated clock, not real-time waits
- Assert that failed jobs produce observable side effects (log entries, metrics, alerts)

# Monitoring

- Track job execution duration, start/end timestamps, and success/fail counts per job name
- Alert on missed schedules — if a job expected every 5 minutes has no run in 10 minutes, fire an alert
- Monitor overlapping executions — concurrent runs of the same job indicate missing overlap protection
- Track retry counts and dead-letter queue depth for failed jobs
- Alert on job duration drift — a job that normally takes 30s suddenly taking 5m signals degradation
- Dashboard showing last-run status per job with time-since-last-success
- Monitor scheduler process health separately from job health (scheduler crash = all jobs stop)

