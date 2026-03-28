## Testing

Verify the ACL translates between bounded contexts without leaking foreign domain concepts.

### Unit Tests

- Assert inbound translation: external model maps to the correct internal domain model
- Assert outbound translation: internal model maps to the correct external representation
- Verify that unknown or malformed external fields are rejected or safely defaulted

### Integration Tests

- Wire the ACL against a stubbed external system and verify end-to-end translation fidelity
- Test schema evolution: introduce a new field in the external model and verify the ACL handles it gracefully

### Failure Injection

- Send payloads with missing required fields and verify the ACL returns structured errors, not leaky exceptions

