# Testing

- Test deserialization of JSON data against Pydantic/dataclass models with missing, extra, and malformed fields
- Fuzz test JSON consumers with randomized payloads to catch KeyError and TypeError at boundaries
- Assert that schema validation rejects unknown fields or provides safe defaults for missing ones
- Test schema evolution by loading data written in a previous schema version into the current model
- Verify that every code path accessing JSON fields goes through a validated model, not raw dict access
- Write contract tests between JSON producers and consumers to detect shape drift early
- Test migration scripts that transform old JSON shapes to the new schema across representative data samples

