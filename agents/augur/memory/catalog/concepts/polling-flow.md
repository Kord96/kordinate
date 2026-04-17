---
description: "Polling flow \u2014 periodic check for state changes or new work"
type: flow-shape
abstraction:
- integration
- lifecycle
status: primary
scope: cross-cutting
relationships:
  related_to:
  - long-polling
  - scheduler
  - webhook
aliases: []
disambiguates_from: []
preferred_over: []
implies: []
anti_signals: []
detector_coverage: none
examples: []
---
# Polling

## Recognition

### Signatures

- `setInterval()` or `setTimeout()` with recurring fetch/check
- Cron jobs or k8s CronJobs that run periodically
- `while True: sleep(N); check()` loops
- Database polling: `SELECT * FROM jobs WHERE status = 'pending' LIMIT N`
- SQS `ReceiveMessage` with `WaitTimeSeconds` (long polling)
- File system watchers checking for new files in a directory
- Health check loops: periodically hitting `/healthz` endpoints
- Polling-based leader election: periodic attempts to acquire a lock
- `last_checked_at` or `cursor` columns tracking polling position

### Confidence

- **high** — explicit periodic loop with configurable interval, idempotent processing, and cursor tracking
- **medium** — cron job or timer-based check without idempotency guarantees
- **low** — ad-hoc `sleep()` loops without structured polling pattern

### Relationship To Other Concepts

- Related to [long-polling](/concepts/long-polling) because long polling is a more efficient specialized form of poll-based interaction.
- Related to [scheduler](/concepts/scheduler) when polling cadence is driven by scheduled jobs or timed loops.
- Related to [webhook](/concepts/webhook) as a push-based alternative that often replaces repeated polling.

### Boundary

Use `polling-flow` when updates are obtained by repeated requests or checks on a cadence instead of by push-based delivery.

Do not use it for one-off retries or monitoring probes that are not the primary interaction pattern.
