---
description: Structured Logging architectural pattern
type: pattern
testable: true
observable: true
graphable: true
abstraction:
- observability
status: primary
scope: cross-cutting
relationships:
  related_to:
  - correlation-id
  - metrics-instrumentation
  - distributed-tracing
aliases: []
disambiguates_from: []
preferred_over: []
implies: []
anti_signals: []
detector_coverage: rich
examples: []
---
# Structured Logging

## Recognition

How to identify this pattern in code.

### Signatures

- JSON log output format instead of plain text lines
- Key-value log fields: `logger.info("event", key=value)`, `log.With("key", value)`
- Libraries: `structlog` (Python), `logrus` (Go), `zap` (Go), `slog` (Go), `pino` (Node), `winston` with JSON transport
- Context binding: `logger = logger.bind(request_id=rid)`, `log.WithFields()`, `logger.With()`
- Log level as a structured field (`"level": "info"`) not a format prefix (`INFO:`)
- Correlation ID attached to every log entry
- Log configuration importing JSON formatter or structured encoder

### Confidence

- **high** -- JSON log formatter configured and context-bound logger used across request lifecycle
- **medium** -- structured logging library imported but log calls still use printf-style formatting
- **low** -- JSON output detected in logs but no explicit structured logging library in dependencies

## Architecture

Look for consistent structured output with contextual fields propagated through the request lifecycle.

### Review Checklist

- All log entries include a correlation/request ID for traceability
- Log fields are typed and consistent across services (not ad-hoc string interpolation)
- Sensitive data (passwords, tokens, PII) is never logged -- redaction is explicit
- Log levels are meaningful: ERROR for actionable failures, WARN for degradation, INFO for business events, DEBUG for troubleshooting
- Logger is bound to request context early and passed through the call chain

### Anti-patterns

- Mixing structured and unstructured logging in the same service
- Logging full request/response bodies without redaction
- Using string formatting inside structured log calls (`logger.info(f"user {user_id}")` instead of `logger.info("user_login", user_id=user_id)`)
- No correlation ID -- structured output with no way to trace a request across log entries

### Relationship To Other Concepts

- Related to [correlation-id](/concepts/correlation-id) because structured fields make request or flow identifiers useful across many log entries.
- Related to [metrics-instrumentation](/concepts/metrics-instrumentation) because both contribute to observability, though logs capture discrete events while metrics summarize behavior.
- Related to [distributed-tracing](/concepts/distributed-tracing) when trace and span identifiers are emitted in structured log fields.

### Boundary

Use `structured-logging` when logs are emitted as machine-readable fields rather than only unstructured text strings.

Do not use it for any logging framework. The key signal is structured event fields intended for parsing and correlation.
