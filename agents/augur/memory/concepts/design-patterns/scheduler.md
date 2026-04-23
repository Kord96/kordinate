---
kind: concept
name: scheduler
signatures: {}
type: pattern
abstraction:
- lifecycle
scope: cross-cutting
status: primary
review_questions:
  threshold: 5
  entries:
  - id: scheduler-cadence-owned-runtime
    prompt: Does a named subsystem own recurring execution on a defined cadence rather
      than just calling sleep or setInterval ad hoc?
    weight: 3
    signals:
    - cron
    - schedule
    - periodic
  - id: scheduler-missed-run-visibility
    prompt: Is there visible handling for missed, delayed, or overlapping scheduled
      runs?
    weight: 2
    signals:
    - missed
    - overlap
    - next run
monitoring:
  applies_to:
  - component
  - flow
  health_signals:
  - name: scheduler.missed_run.rate
    description: Frequency of scheduled executions that do not start within the expected
      interval.
  - name: scheduler.run.delay
    description: Delay between the expected schedule time and the actual start time.
  - name: scheduler.overlap.rate
    description: Rate of concurrent overlapping runs for jobs that are expected to
      serialize.
  business_metrics:
  - name: scheduler.jobs_completed_per_interval
    description: Number of scheduled jobs that complete within each expected execution
      window.
  - name: scheduler.backlog_cleared_per_run
    description: Amount of queued or pending work cleared by each scheduled execution
      cycle.
  gaps:
  - Without missed-run and delay visibility, periodic work can silently stop meeting
    its intended cadence.
family: design-patterns
---

# Explanation

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
