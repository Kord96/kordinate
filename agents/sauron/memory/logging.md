---
description: Structured logging standards across all projects
---
# Logging

Structured logging standards across all projects.

## Architecture

```
App → structlog (JSON) → stdout → Loki/Alloy → Grafana
```

All projects use **structlog** with JSON output in production and colored console in dev. The log pipeline is:
1. App emits structured JSON to stdout
2. Container runtime / systemd captures stdout
3. Loki (via Alloy or direct) ingests and indexes
4. Grafana dashboards and alerts query Loki

### Setup Pattern

Every project needs a `configure_logging()` call at startup that sets up:
- structlog with JSON renderer (production) or ConsoleRenderer (dev)
- stdlib bridge so library logs also get structured
- Process-level context binding (service name, consumer ID)

Reference implementation: `klog/` in this agent's directory — context binding, validation, filtering, trace IDs, log capture for testing. Use as a pattern to generate project-specific logging code.

### Log Levels

Use levels consistently across all projects:

| Level | When | Examples |
|-------|------|----------|
| **debug** | Internal details, only useful during development | Buffer contents, query plans, parsed values |
| **info** | Normal operational events | Service started, flush completed, batch processed |
| **warning** | Degraded but recoverable | Slow operation, high retry count, approaching limits |
| **error** | Failed operation that needs attention | Connection lost, data corruption, unhandled exception |

### Event Naming

- Use **snake_case** event names: `flush_complete`, `connection_lost`, `batch_processed`
- Use **past tense** for completed actions: `message_consumed`, `cache_refreshed`
- Use **present tense** for ongoing states: `processing_slow`, `disk_full`
- Prefix with component name when ambiguous: `dns_error_rate_high`, `kafka_lag_growing`

### Dimensions (Key-Value Fields)

Always include dimensions that enable filtering and correlation:

```python
# Good — filterable, correlatable
logger.info("flush_complete", consumer="graph-domain", rows=1500, duration_s=2.3)

# Bad — unstructured, unfilterable
logger.info(f"Flushed 1500 rows in 2.3s for graph-domain")
```

Standard dimensions:
- `consumer` / `service`: Which service/consumer emitted the log
- `duration_s`: How long an operation took (always in seconds, rounded)
- `count` / `rows` / `messages`: Quantity processed
- `error`: Error message string (for warning/error level)
- `attempt` / `max_retries`: Retry context

### Context Binding

Bind dimensions that apply to all logs within a scope:

```python
# Process-level (set once at startup)
structlog.contextvars.bind_contextvars(consumer="graph-domain")

# Scope-level (if using klog pattern)
with log.context(batch_id="abc123", stage="enrichment"):
    log.info("processing")  # auto-includes batch_id + stage
```

### Rate Limiting

For high-frequency events, rate-limit logs to avoid flooding:

```python
_last_report = 0

def on_error(error):
    nonlocal _last_report
    now = time.monotonic()
    if now - _last_report > 60:  # at most once per minute
        logger.warning("errors_in_batch", error=str(error))
        _last_report = now
```

### Threshold-Based Levels

Operational metrics should log at appropriate levels based on thresholds:

```python
elapsed = time.monotonic() - t0
if elapsed > 600:
    logger.warning("operation_slow", duration_s=round(elapsed, 1), threshold_s=600)
elif elapsed > 300:
    logger.warning("operation_slow", duration_s=round(elapsed, 1), threshold_s=300)
else:
    logger.info("operation_complete", duration_s=round(elapsed, 1))
```

### What NOT to Log

- Don't log at info level in hot loops (per-message, per-row)
- Don't log sensitive data (passwords, tokens, PII)
- Don't use f-strings in log events — use dimensions instead
- Don't log stack traces at warning level — use error/exception
- Don't duplicate metrics as logs — use Prometheus for counters/gauges
