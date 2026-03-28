---
description: ETL — monitoring guidance
curated: true
scope: global
preloaded: none
---
## Monitoring

Track job execution, per-stage throughput, and error rates to detect pipeline degradation across extract, transform, and load phases.

### Key Metrics

- `etl_job_duration_seconds` (histogram) — end-to-end job execution time
- `etl_records_extracted_total` (counter) — records pulled per extraction run
- `etl_transform_errors_total` (counter) — records that failed transformation
- `etl_records_loaded_total` (counter) — records successfully written to the target store
- `etl_checkpoint_lag_seconds` (gauge) — time since last successful checkpoint

### Alerts

- Job duration exceeding expected window (pipeline slowing down)
- Transform error rate exceeding threshold (bad source data or broken logic)
- Checkpoint lag growing (jobs failing silently without advancing bookmark)
- Extracted-to-loaded record ratio diverging (data loss between stages)
