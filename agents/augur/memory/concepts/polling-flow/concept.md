---
description: Polling flow — periodic check for state changes or new work
type: flow-shape
abstraction: [integration, lifecycle]
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
