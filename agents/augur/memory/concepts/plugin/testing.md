---
description: Plugin Architecture — testing guidance
---
## Testing

Confirm that the core runs cleanly without plugins and that plugins conform to the published interface contract.

### Unit Tests

- Test plugin registration — verify that registering a valid plugin adds it to the registry and duplicate registration is handled
- Assert interface compliance: create a minimal plugin implementation and verify all required methods are callable with expected signatures
- Test core functionality with zero plugins loaded — confirm graceful degradation, not crashes
- Verify plugin lifecycle hooks (init, start, stop) are called in the correct order

### Integration Tests

- Load multiple plugins simultaneously and verify they do not interfere with each other
- Test plugin hot-reload or re-registration if supported — verify the core picks up the new version
- Test that a plugin built against an older interface version is either compatible or cleanly rejected with a version mismatch error

### Failure Injection

- Inject a plugin that throws during initialization and verify the core starts without it and logs the failure
- Simulate a plugin that blocks indefinitely in its stop hook and verify the core enforces a shutdown timeout
- Load a plugin that panics during request handling and confirm the core isolates the failure without crashing
