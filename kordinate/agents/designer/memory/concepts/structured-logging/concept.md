---
description: Structured Logging architectural pattern
type: pattern
testable: true
observable: true
curated: true
scope: global
preloaded: none
graphable: true
abstraction: [observability]
---
# Structured Logging

## Recognition

How to identify this pattern in code.

### Signatures

- JSON log output format instead of plain text lines
- Key-value log fields: `logger.info("event", key=value)`, `log.With("key", value)`
- Libraries: `structlog` (Python), `logrus` (Go), `zap` (Go), `slog` (Go stdlib), `zerolog` (Go), `pino` (Node), `winston` with JSON transport
- Go stdlib: `log/slog` import with `slog.Info("msg", "key", value)`, `slog.With("key", value)` -- standard library structured logging since Go 1.21
- Context binding: `logger = logger.bind(request_id=rid)`, `log.WithFields()`, `logger.With()`
- Log level as a structured field (`"level": "info"`) not a format prefix (`INFO:`)
- Correlation ID attached to every log entry
- Log configuration importing JSON formatter or structured encoder
- Java: `net.logstash.logback.encoder.LogstashEncoder`, `LoggingEventCompositeJsonEncoder` for JSON log output
- Java: MDC (Mapped Diagnostic Context) usage with `MDC.put()` for request-scoped structured fields
- Java: Log4j2 `JsonLayout`, `JsonTemplateLayout` configuration
- Java: Custom `LogEntry` or `LogEvent` classes with discrete structured fields beyond simple message strings

### Negative signals (not sufficient for detection)

- Mere SLF4J `LoggerFactory.getLogger()` or `log.info()` usage is standard Java logging, not structured logging
- Using `Logger` without JSON output format or MDC context binding is unstructured (plain text) logging

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
