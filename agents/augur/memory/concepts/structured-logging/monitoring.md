---
description: Structured Logging — monitoring guidance
---
## Monitoring

Track log pipeline health, format compliance, and field quality to maintain reliable observability.

### Key Metrics

- `log_entries_total` (counter) — log volume per service and severity level (ERROR, WARN, INFO, DEBUG)
- `log_missing_correlation_id_total` (counter) — entries without a request/correlation ID, breaking traceability
- `log_unstructured_entries_total` (counter) — non-JSON entries in a service that should emit only structured output
- `log_ingestion_lag_seconds` (gauge) — delay between log emission and availability in the aggregator
- `log_pipeline_drop_rate` (counter) — log entries dropped or failed to parse in the ingestion pipeline
- `log_field_cardinality` (gauge) — distinct values per indexed field, detects unbounded fields that overwhelm indexing

### Alerts

- Sudden spike in ERROR or WARN log volume (emerging incident)
- Log entries appearing without correlation IDs (traceability gap)
- Unstructured log entries detected in a service expected to emit JSON only
- Log ingestion pipeline lag or drop rate exceeding acceptable thresholds
- Sensitive data patterns (tokens, passwords, PII) detected in log entries
