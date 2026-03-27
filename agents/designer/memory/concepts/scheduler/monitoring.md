---
description: Cron/Scheduler — monitoring guidance
type: supplementary
curated: true
scope: global
preloaded: none
---
# Monitoring

- Track job execution duration, start/end timestamps, and success/fail counts per job name
- Alert on missed schedules — if a job expected every 5 minutes has no run in 10 minutes, fire an alert
- Monitor overlapping executions — concurrent runs of the same job indicate missing overlap protection
- Track retry counts and dead-letter queue depth for failed jobs
- Alert on job duration drift — a job that normally takes 30s suddenly taking 5m signals degradation
- Dashboard showing last-run status per job with time-since-last-success
- Monitor scheduler process health separately from job health (scheduler crash = all jobs stop)
