---
description: Cron/Scheduler architectural pattern
type: pattern
testable: true
observable: true
curated: true
scope: global
preloaded: none
graphable: true
abstraction: [lifecycle]
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

**Not this pattern:** `setInterval` / `setTimeout` in JavaScript/TypeScript for UI debouncing, animation frames, polling intervals, or retry delays is not the scheduler pattern. The scheduler pattern requires task registration with time-based triggers (cron expressions, fixed intervals) and lifecycle management (start, stop, list scheduled jobs). A single `setInterval` call in a utility function is just a timer.

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
