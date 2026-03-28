## Testing

Verify feature pipelines produce correct values and that online/offline serving returns consistent results.

### Unit Tests

- Test each feature transformation function with known inputs and assert exact expected outputs
- Verify null handling: missing source data should produce documented default values, not propagate nulls silently
- Assert that feature types match the declared schema (float, int, string, embedding) after transformation
- Test time-window aggregations with edge cases: empty windows, single-element windows, windows spanning DST changes

### Integration Tests

- Run the full feature pipeline on a sample dataset and compare output against a golden reference
- Fetch the same entity's features from both the online and offline store and verify consistency within the expected staleness window
- Test point-in-time correctness: features retrieved for a historical timestamp should reflect only data available at that time

### Online/Offline Parity

- Compare model predictions using online-served features vs offline-computed features for the same input set — divergence indicates a training-serving skew

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

## Deployment

Coordinate feature pipeline, store, and serving layer deployments to avoid serving stale or incompatible features.

### Rollout Implications

- Deploy feature transformation pipeline updates before model updates that depend on new features — the store must contain the features before the model requests them
- Backfill new features before switching models to use them — missing feature values cause null defaults or inference errors
- Rolling updates to the serving layer may briefly increase latency during cache warming — monitor serving latency during rollout
- If changing feature schemas (new columns, type changes), update offline and online stores in lockstep

### Pre-deploy Checklist

- Verify feature freshness is within SLA for all feature groups the target model depends on
- Confirm online store connectivity and latency from the model serving environment

