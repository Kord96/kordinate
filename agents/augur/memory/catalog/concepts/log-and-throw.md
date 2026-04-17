---
description: Log and Throw anti-pattern
type: anti-pattern
graphable: false
status: supporting
scope: backend
relationships:
  related_to:
  - swallowed-exception
  - structured-logging
  - correlation-id
aliases: []
disambiguates_from: []
preferred_over: []
implies: []
anti_signals: []
detector_coverage: partial
examples: []
---
# Log and Throw

## Recognition

How to identify this anti-pattern in code.

### Signatures

- `logger.error(e); raise e` or `catch(e) { log(e); throw e; }` in the same block
- Same exception logged at multiple layers as it propagates up the call stack
- Duplicate error entries in logs for a single failure, differing only by the logging class name
- `catch` blocks that log the full stack trace and then rethrow the same exception unchanged
- Error counts in monitoring dashboards that are multiples of actual failure occurrences

### Confidence

- **high** -- a catch block both logs the exception at error level and rethrows it, and callers do the same
- **medium** -- a catch block logs the exception and rethrows, but only one layer in the call stack does this
- **low** -- a catch block logs at warn/info level and rethrows, which may be intentional for tracing

## Impact

Log noise multiplies, error counts become meaningless, and operators waste time correlating duplicate entries for the same root failure.

### Symptoms

- A single user-facing error produces 3-5 identical log entries at different stack depths
- Error rate dashboards show inflated numbers that do not match actual incident counts
- On-call engineers waste time during incidents determining whether multiple log lines represent one failure or many
- Log storage costs increase due to redundant error messages
- Alert thresholds must be set artificially high to avoid false alarms from the inflated error counts

### Remediation

- Choose one: log the error OR rethrow it, not both at the same level
- Let exceptions propagate naturally and log them once at the boundary where they are handled (top-level handler, API middleware)
- If intermediate layers need to add context, wrap the exception in a new one with additional information instead of logging
- Use structured logging with correlation IDs so a single log entry at the boundary provides full traceability
- Audit the codebase for catch-log-rethrow patterns and remove the redundant log statements

### Relationship To Other Concepts

- Related to [swallowed-exception](/concepts/swallowed-exception) because both distort error observability, though log-and-throw duplicates failure records instead of hiding them entirely.
- Related to [structured-logging](/concepts/structured-logging) because the better alternative is usually one well-formed boundary log with enough context.
- Related to [correlation-id](/concepts/correlation-id) because correlation makes single-point logging workable without repeating the same exception at every layer.

### Boundary

Use `log-and-throw` when a layer logs an exception and then rethrows it unchanged, creating redundant error noise up the stack.

Do not use it when a layer adds real context by wrapping the exception or when it is the terminal handling boundary.
