---
kind: concept
name: log-spam
signatures: {}
source:
  memory_concept: memory/catalog/concepts/log-spam.md
type: anti-pattern
abstraction: []
scope: cross-cutting
status: supporting
---

# Explanation

## Recognition

How to identify this anti-pattern in code.

### Signatures

- `logger.info()` or `logger.debug()` inside `for`/`while` loops
- Log statements in hot paths (request handlers logging every field)
- Thousands of log lines per second from a single service
- No rate limiting on log events (`logger.warning()` called unconditionally on every request)
- Log level set to DEBUG in production configuration
- Logging full request/response bodies at INFO level

### Confidence

- **high** -- log statement inside a loop body that iterates over unbounded input, confirmed by log volume metrics exceeding 1k lines/sec per pod
- **medium** -- `logger.info()` or `logger.debug()` call inside a `for`/`while` loop without a conditional guard or sampling
- **low** -- log level set to DEBUG or TRACE in a production config file, or verbose logging enabled without a feature flag

## Impact

Log storage costs explode, Loki/ELK clusters are overwhelmed, and real signals are lost in noise.

### Symptoms

- Log aggregation system (Loki, Elasticsearch) experiences ingestion lag or drops
- Log storage costs grow disproportionately to traffic
- Searching logs for a specific error takes minutes because of volume
- Alerting on log patterns fires constantly due to noise
- Disk I/O pressure on nodes running log shippers

### Remediation

- Move debug-level logging behind a conditional or feature flag, never enable unconditionally in production
- Use structured logging with sampling for high-frequency events (`log every Nth` or probabilistic sampling)
- Replace per-iteration logging with a summary log after the loop (`processed N items in Xms`)
- Set appropriate log levels per environment: ERROR/WARN in production, DEBUG only in development
- Add rate limiting to log emitters for known high-volume paths

### Relationship To Other Concepts

- Related to [structured-logging](/concepts/structured-logging) because structured logging often reduces noise by making fewer logs more useful.
- Related to [metrics-instrumentation](/concepts/metrics-instrumentation) because repeated per-event logs are sometimes a poor substitute for aggregate metrics.
- Related to [missing-log-context](/concepts/missing-log-context) because noisy logs are often also low-signal when context is missing.

### Boundary

Use `log-spam` when excessive low-value logging creates noise, cost, or operational blindness.

Do not use it for simply verbose debugging output in development. The key issue is harmful production or architectural logging behavior.
