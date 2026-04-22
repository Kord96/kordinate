---
kind: concept
name: missing-log-context
signatures: {}
source:
  memory_concept: memory/catalog/concepts/missing-log-context.md
type: anti-pattern
abstraction: []
scope: cross-cutting
status: supporting
---

# Explanation

## Recognition

How to identify this anti-pattern in code.

### Signatures

- Log messages with no request ID or correlation ID attached
- Bare `logger.error("failed")` with no structured fields or exception info
- No `structlog.bind()`, `MDC.put()`, or equivalent context binding at request entry
- Impossible to trace a single request across multiple log lines
- Log messages that omit the operation, entity, or input that caused the failure
- No middleware or decorator that injects trace/request IDs into the logging context

### Confidence

- **high** -- error log lines contain only a message string with no structured fields, and there is no request-scoped context binding anywhere in the request lifecycle
- **medium** -- some log calls include context but others in the same service do not, leading to gaps when correlating across calls
- **low** -- logging framework is configured but individual log statements omit key identifiers like entity IDs or operation names

## Impact

Debugging requires guesswork, and incident resolution takes significantly longer because logs cannot be correlated.

### Symptoms

- On-call engineers cannot trace a user-reported error to a specific request
- Log searches return ambiguous results matching multiple unrelated events
- Correlating logs across microservices requires manual timestamp alignment
- Post-incident reviews cite "insufficient logging" as a contributing factor
- Distributed tracing tools show gaps where log context was not propagated

### Remediation

- Add middleware or a request interceptor that binds a request ID and correlation ID to every log entry for the request lifecycle
- Use structured logging (structlog, logfmt, JSON logging) so every log line includes machine-parseable context fields
- Require a minimum set of context fields on all log calls: request ID, operation name, and relevant entity IDs
- Propagate trace context (W3C Trace Context, X-Request-ID) across service boundaries and bind it to the logger
- Add a linting rule that flags bare `logger.error("string")` calls without structured arguments

See also: structured-logging, correlation-id patterns

### Relationship To Other Concepts

- Related to [structured-logging](/concepts/structured-logging) because this concept commonly appears alongside it or is clarified by contrast with it.

### Boundary

Use `missing-log-context` when the important observation is this specific recurring architectural failure mode within a cross-cutting architectural concern that can span multiple layers or services.

Do not use it just because a few signatures match; the surrounding responsibilities and architectural role should line up too.
