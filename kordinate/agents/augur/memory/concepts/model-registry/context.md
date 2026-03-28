## Testing

Verify model versioning, stage transitions, and artifact integrity through the full lifecycle.

### Unit Tests

- Register a model version and assert it appears in the registry with correct metadata (metrics, parameters, lineage)
- Transition a model through stages (staging, production, archived) and verify each transition is recorded
- Load a model by name and stage and assert the correct version and artifact are returned

### Integration Tests

- Register a model, promote to production, and verify a serving endpoint resolves to the correct artifact
- Attempt to overwrite an existing model version and verify it is rejected (immutability)
- Archive a model and confirm it is no longer served but remains available for audit

### Validation Tests

- Register a model without required metadata (metrics, lineage) and assert the registry rejects or warns
- Promote a model that fails validation gates and verify the transition is blocked

## Monitoring

Track model lifecycle transitions, serving health, and registry availability.

### Key Metrics

- `model_versions_registered_total` (counter) — new model versions added to the registry
- `model_stage_transitions_total` (counter) — stage changes (staging, production, archived) per model
- `model_serving_version` (info gauge) — currently serving model version, exposed as a label
- `model_registry_latency_seconds` (histogram) — time to load or register a model version

### Alerts

- No new model versions registered for an unexpectedly long period (training pipeline stalled)
- Model promoted to production without passing validation gates (if enforcement is advisory, not blocking)
- Registry unavailable or latency spiking (serving cannot resolve model versions)
- Model in production stage with no recorded training metrics or data lineage

