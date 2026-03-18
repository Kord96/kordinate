# klog — Logging Perspective

Structured JSON logging library. Reference implementation for all project logging.

## Purpose

structlog-based with session IDs, trace context, field filtering, dimension validation, and async batched API log pushing.

## Key Components for Monitoring

| Component | Role |
|-----------|------|
| configure_logging | Setup — ensure projects call this once at startup |
| log_context | Scope binding — verify dimension consistency |
| log_capture | Test helper — use in tests to assert log output |
| APIPushHandler | Async HTTP push — monitor for failures/backpressure |

## What to Validate

- Is configure_logging called at startup with correct renderer (JSON for prod)?
- Are log levels used correctly per logging.md standards?
- Are event names snake_case and consistent?
- Are dimensions structured (not f-string interpolation)?
- Is log_capture used in tests to verify critical log events?
- Are noisy library loggers (kafka, urllib3) suppressed?

## Log Review Checklist

- Inconsistent event names across components
- Missing dimensions (consumer, duration_s, count)
- Wrong log levels (info in hot loops, warning without threshold)
- Unstructured f-strings instead of dimension kwargs
- Missing rate limiting on high-frequency warnings

## Install

```
pip install klog
```
