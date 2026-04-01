---
description: Structured Logging — testing guidance
type: supplementary
---
# Testing

- Test that all log entries are valid JSON with required fields (level, timestamp, correlation_id, message)
- Verify that sensitive data (passwords, tokens, PII) is redacted or absent from log output
- Test context binding: a correlation ID bound at request entry appears in all subsequent log entries
- Assert that log levels are meaningful — ERROR for actionable failures, not for expected conditions
- Test that string formatting is not used inside structured log calls (field=value, not f-string)
- Verify that log output does not mix structured and unstructured formats within a service
- Test log output under error conditions to confirm stack traces are captured as structured fields
- Assert that log field names are consistent across services (agreed-upon schema, not ad-hoc)
