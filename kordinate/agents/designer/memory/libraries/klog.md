---
description: klog library reference
curated: true
scope: global
---
# klog

Structured JSON logging with context binding and validation. structlog-based. `pip install klog`.

## Architecture

Pattern: `configure once -> log everywhere`. Session IDs, trace context, field filtering, dimension validation, async batched API log pushing.

| Class | Role |
|-------|------|
| configure_logging | One-time setup — structlog processors, handlers, filters |
| log_context | Context manager for dimension binding (nested, inheritable) |
| trace_context | Context manager for service + trace_id binding |
| log_capture | Test helper — capture logs for assertions |
| APIPushHandler | Async batched HTTP log pushing (stdlib only) |

Review: configure_logging called once at startup? log_context for scope binding? stdlib loggers bridged? APIPushHandler only for external APIs (not Loki)?

## Monitoring

| Component | What to validate |
|-----------|-----------------|
| configure_logging | Called at startup with correct renderer (JSON for prod) |
| log_context | Dimension consistency across scopes |
| log_capture | Used in tests to assert critical log events |
| APIPushHandler | Monitor for failures/backpressure |

Log review: inconsistent event names, missing dimensions (consumer, duration_s, count), wrong levels, unstructured f-strings, missing rate limiting on high-frequency warnings.

## Deployment

Library dependency, not a standalone service — no pods to manage. All Python services include klog in requirements. configure_logging must be called at startup for Alloy/Loki ingestion. APIPushHandler needs network access — check NetworkPolicy.

Deploy method: git-branch (trusted publishing via GitHub Actions OIDC).

## Testing

- Are log levels correct per logging standards?
- Are event names snake_case and consistent?
- Are dimensions structured (not f-string interpolation)?
- Are noisy library loggers (kafka, urllib3) suppressed?
- Is log_capture used in tests?
