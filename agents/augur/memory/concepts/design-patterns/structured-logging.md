---
kind: concept
name: structured-logging
signatures:
  concept: structured-logging
  positive:
    strong:
    - structured logging library with JSON or key-value log calls
    - context-bound logger usage across request lifecycle
    medium:
    - structured logger configured but mixed call styles
    weak:
    - JSON-like strings without clear structured logger usage
  negative:
  - printf-style logging only
  - string interpolation inside nominally structured log calls
  notes:
  - Correlation context raises confidence materially.
type: pattern
abstraction:
- observability
scope: cross-cutting
status: primary
review_questions:
  threshold: 4
  entries:
  - id: structured-logging-kv
    prompt: Do log calls carry structured key-value fields or JSON formatting rather
      than plain text interpolation?
    weight: 2
    signals:
    - logger.bind
    - WithFields
    - pino
  - id: structured-logging-context
    prompt: Is request or correlation context propagated through log calls?
    weight: 2
    signals:
    - request_id
    - correlation_id
monitoring:
  applies_to:
  - component
  - system
  health_signals:
  - name: structured_log.error.rate
    description: Error log rate with structured context preserved for aggregation.
  - name: missing_log_context.rate
    description: Frequency of logs missing expected request, trace, or correlation
      identifiers.
  business_metrics: []
  gaps:
  - If structured context is inconsistent, downstream monitoring and incident triage
    quality degrades quickly.
family: design-patterns
---

# Explanation

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
