---
description: Feature Store — monitoring guidance
type: supplementary
---
## Monitoring

Track feature freshness, serving latency, and pipeline health to ensure models receive correct, timely features.

### Key Metrics

- `feature_freshness_seconds` (gauge) — time since the last update for each feature group
- `feature_serving_latency_seconds` (histogram) — latency of online feature retrieval requests
- `feature_pipeline_runs_total` (counter) — successful and failed feature computation pipeline runs
- `feature_null_rate` (gauge) — percentage of null/missing values per feature, by entity

### Alerts

- Feature freshness exceeding SLA (stale features being served to models)
- Serving latency above p99 threshold (online inference impacted)
- Feature null rate spike (upstream data source issue or broken transformation pipeline)
