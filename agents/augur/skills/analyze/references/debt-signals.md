# Debt Signals

Use this reference when turning semantic findings into debt or risk observations.

## High-Signal Structural Debt

- missing fallback or resilience around critical calls
- retry on non-idempotent operations
- business logic in handlers
- direct infrastructure access from boundary layers
- shared mutable state across unrelated domains

## Cross-Cutting Signals

- hardcoded credentials or production config
- bare exception handling
- missing error handling on external calls
- missing health endpoints for long-running services
- no structured logging
- large clusters of TODO or FIXME markers

## Reporting

- group repeated instances into one finding when they share a root cause
- prioritize by severity, blast radius, and ease of remediation
