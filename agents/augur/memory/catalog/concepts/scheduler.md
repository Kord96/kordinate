---
description: Cron/Scheduler architectural pattern
type: pattern
testable: true
observable: true
graphable: true
abstraction:
- lifecycle
status: primary
scope: cross-cutting
relationships:
  related_to:
  - batch-processing
  - leader-election
  - workflow-engine
aliases: []
disambiguates_from: []
preferred_over: []
implies: []
anti_signals: []
detector_coverage: partial
examples: []
---
# Cron/Scheduler

## Recognition

How to identify this pattern in code.

### Signatures

- Cron expressions in config files or decorators (`"0 */5 * * *"`, `@crontab`)
- `APScheduler`, `schedule`, `celery.beat`, `node-cron`, `Quartz` library imports
- `@scheduled`, `@periodic_task`, `@cron` decorators on functions
- Kubernetes `CronJob` resources in manifests
- Periodic task registration at application startup
- Time-based trigger configuration in YAML, JSON, or environment variables
- Functions named `*_job`, `*_task`, `run_periodic_*`, `scheduled_*`

### Confidence

- **high** -- Cron expressions with a scheduler library, registered periodic tasks, and explicit job lifecycle management
- **medium** -- Kubernetes CronJob manifests or `time.sleep` loops with periodic execution, but no formal scheduler library
- **low** -- Manual `setInterval` / `time.sleep` polling without any scheduler framework or cron expression

## Architecture

Look for time-based triggers that invoke tasks on a recurring schedule with proper lifecycle management.

### Review Checklist

- Schedules are configurable (not hardcoded cron strings buried in code)
- Overlapping executions are handled (skip if previous run is still active, or queue)
- Failed jobs have retry logic or dead-letter handling
- Job execution is observable (start/end logging, duration metrics)
- Timezone handling is explicit and consistent across all schedules
- Graceful shutdown waits for in-progress jobs to complete

### Anti-patterns

- Hardcoded sleep loops used instead of a scheduler library
- No overlap protection -- long-running jobs stack up on each trigger
- Silent failure -- jobs fail without logging, alerting, or retry
- Schedule drift from using relative delays (`sleep(300)`) instead of wall-clock cron expressions

### Relationship To Other Concepts

- Related to [batch-processing](/concepts/batch-processing) because scheduled execution often drives batch jobs.
- Related to [leader-election](/concepts/leader-election) when only one instance should execute a scheduled task in a distributed deployment.
- Related to [workflow-engine](/concepts/workflow-engine) when scheduled triggers start or resume longer-running orchestrated work.

### Boundary

Use `scheduler` when work is triggered by time-based or calendar-based rules rather than direct user or event initiation.

Do not use it for arbitrary background work. The key signal is time-based triggering.
