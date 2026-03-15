# klog — Design Perspective

Structured JSON logging with context binding and validation. structlog-based.

## Pattern

`configure once -> log everywhere`

Session IDs, trace context, field filtering, dimension validation, and async batched API log pushing.

## Key Classes

| Class | Role |
|-------|------|
| Logger | Structured logger with context integration and extension hooks |
| configure_logging | One-time setup — structlog processors, handlers, filters |
| log_context | Context manager for dimension binding (nested, inheritable) |
| trace_context | Context manager for service + trace_id binding |
| log_capture | Test helper — capture logs for assertions |
| APIPushHandler | Async batched HTTP log pushing (stdlib only) |

## When to Use

- Setting up structured logging in any Python service
- Adding trace context and correlation IDs
- Filtering logs by field values at runtime
- Pushing logs to an HTTP API endpoint
- Capturing logs in tests for assertions

## Architecture Review Checklist

- Is configure_logging called once at startup (not per-module)?
- Is log_context used for scope binding instead of manual field passing?
- Are stdlib loggers bridged so library logs are also structured?
- Is APIPushHandler used only for external API targets (not Loki — Alloy handles that)?

## Install

```
pip install klog
```
