# Saga — Design Perspective

Look for correct compensation logic and failure handling across distributed steps.

## Review Checklist

- Each step has a corresponding compensating action
- Compensation is idempotent (safe to retry on partial failure)
- Saga coordinator tracks step state (pending, completed, compensated)
- Timeout handling exists for steps that may hang

## Anti-patterns

- Missing compensation for one or more steps (partial rollback)
- Compensating actions that can themselves fail without retry
- Using sagas where a simple two-phase operation would suffice
