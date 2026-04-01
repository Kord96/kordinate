---
description: Structured Logging — monitoring guidance
type: supplementary
---
# Monitoring

- Track log volume per service and level — sudden spikes in ERROR or WARN indicate emerging issues
- Alert on log entries missing correlation/request IDs, which break traceability
- Monitor log ingestion pipeline health: lag, drop rate, and parsing errors in the log aggregator
- Alert on unstructured log entries appearing in a service that should emit only JSON
- Track log field cardinality — unbounded field values (raw user input) can overwhelm log indexing
- Dashboard showing error rate derived from structured log entries correlated with service health
- Monitor for sensitive data in logs by scanning for patterns matching tokens, passwords, or PII
