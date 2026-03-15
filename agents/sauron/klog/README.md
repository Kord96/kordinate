# klog

Structured JSON logging with context binding and validation.

## Structure

| File | Lines | What it does | When to use |
|------|-------|-------------|-------------|
| `core.py` | ~270 | `configure_logging`, `Logger`, `log_context` | Every project |
| `extensions.py` | ~300 | Filters, validation, trace context, custom processors | When you need fine-grained control |
| `testing.py` | ~70 | `log_capture` for assertions in tests | Testing only |
| `api_push.py` | ~115 | Async batched HTTP log pushing | Infrastructure (needs LOG_API_URL) |

## Quick start

```python
from klog import log, configure_logging

configure_logging(app_name="my_service")
log.info("processing", phase="startup", items=10)

with log.context(stage="execute"):
    log.info("step")  # Has stage
```

## For most projects, you only need core.py

The `configure_logging` + `log` + `log.context` pattern covers 90% of use cases.
Extensions are wired in automatically when available — you don't need to import them
unless you want fine-grained control (filters, trace IDs, validation).

## Environment variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `LOG_LEVEL` | `INFO` | DEBUG, INFO, WARNING, ERROR |
| `LOG_FILTER` | — | Include only matching: `field=value,field=value` |
| `LOG_EXCLUDE` | — | Exclude matching: `field=value,field=value` |
| `LOG_API_URL` | — | API endpoint for log pushes (enables api_push) |
