# Testing

- Test that all log entries are valid JSON with required fields (level, timestamp, correlation_id, message)
- Verify that sensitive data (passwords, tokens, PII) is redacted or absent from log output
- Test context binding: a correlation ID bound at request entry appears in all subsequent log entries
- Assert that log levels are meaningful — ERROR for actionable failures, not for expected conditions
- Test that string formatting is not used inside structured log calls (field=value, not f-string)
- Verify that log output does not mix structured and unstructured formats within a service
- Test log output under error conditions to confirm stack traces are captured as structured fields
- Assert that log field names are consistent across services (agreed-upon schema, not ad-hoc)

# Monitoring

- Track log volume per service and level — sudden spikes in ERROR or WARN indicate emerging issues
- Alert on log entries missing correlation/request IDs, which break traceability
- Monitor log ingestion pipeline health: lag, drop rate, and parsing errors in the log aggregator
- Alert on unstructured log entries appearing in a service that should emit only JSON
- Track log field cardinality — unbounded field values (raw user input) can overwhelm log indexing
- Dashboard showing error rate derived from structured log entries correlated with service health
- Monitor for sensitive data in logs by scanning for patterns matching tokens, passwords, or PII

