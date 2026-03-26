---
description: Insecure Deserialization — testing guidance
type: supplementary
curated: true
scope: global
preloaded: none
---
## Testing

Verify that untrusted input is never deserialized with unsafe functions and payloads are schema-validated.

### Unit Tests

- Assert that deserialization uses safe loaders (`yaml.safe_load`, JSON, MessagePack), not `pickle.loads` or `eval`
- Submit a crafted pickle or YAML payload with a `__reduce__` exploit and verify it is rejected
- Validate that deserialized data is checked against a schema (Pydantic, JSON Schema) before use

### Static Analysis

- Scan for `pickle.loads`, `eval()`, `exec()`, `yaml.load()` without SafeLoader, and `unserialize()` on untrusted input
- Add a CI lint rule that flags unsafe deserialization functions in non-test code

### Integration Tests

- Send a malformed serialized payload to an API endpoint and verify it returns a validation error, not a crash
- Confirm that switching from an unsafe deserializer to a safe one does not break any legitimate data flows
