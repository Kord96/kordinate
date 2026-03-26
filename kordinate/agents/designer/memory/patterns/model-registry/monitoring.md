---
description: Model Registry — monitoring guidance
type: supplementary
curated: true
scope: global
preloaded: none
---
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
