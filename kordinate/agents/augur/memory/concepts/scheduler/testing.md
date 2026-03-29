---
description: Cron/Scheduler — testing guidance
type: supplementary
---
# Testing

- Unit test job logic independently from the scheduler — inject a fake clock and trigger manually
- Test overlap protection by simulating a long-running job and verifying the next trigger is skipped or queued
- Test retry behavior by injecting failures and asserting retry count, backoff intervals, and dead-letter handling
- Verify graceful shutdown waits for in-progress jobs before terminating
- Test timezone handling with explicit timezone fixtures — daylight saving transitions cause real bugs
- Test cron expression parsing against known edge cases (leap years, month boundaries, `*/5` vs `5`)
- Integration test the full schedule-to-execution path with an accelerated clock, not real-time waits
- Assert that failed jobs produce observable side effects (log entries, metrics, alerts)
