---
description: Cron/Scheduler — monitoring guidance
---
## Monitoring

Track job execution health, schedule adherence, and scheduler process availability.

### Key Metrics

- `scheduler_job_duration_seconds` (histogram) — execution time per job name, detects performance drift
- `scheduler_job_runs_total` (counter) — job executions partitioned by job name and status (success/failure)
- `scheduler_missed_schedules_total` (counter) — expected runs that did not fire within the tolerance window
- `scheduler_overlapping_runs` (gauge) — concurrent executions of the same job (should be 0 with overlap protection)
- `scheduler_retry_total` (counter) — retry attempts per job, indicates transient or persistent failures
- `scheduler_dead_letter_queue_depth` (gauge) — failed jobs awaiting manual intervention

### Alerts

- Job has not run within twice the expected schedule interval (missed schedule)
- Job duration exceeds historical p99 by a significant margin (execution drift)
- Overlapping executions detected for a job that should run exclusively
- Scheduler process health check failing (all jobs stop if the scheduler crashes)
- Dead-letter queue depth growing steadily (unresolved job failures)
