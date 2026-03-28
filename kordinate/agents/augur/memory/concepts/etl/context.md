## Testing

Verify transform logic purity, bookmark tracking accuracy, and idempotent load behavior across repeated runs.

### Unit Tests

- Test transform functions as pure functions — given the same input records, assert identical output with no side effects
- Verify bookmark tracking: after a successful run, the bookmark advances; after a failed run, it remains at the previous position
- Test schema validation between extract and transform — confirm malformed records are rejected with descriptive errors
- Assert that the load phase handles duplicate keys gracefully (upsert semantics, not duplicate inserts)

### Integration Tests

- Run a full extract-transform-load cycle against real sources and sinks, then verify row counts and data integrity
- Execute two consecutive incremental runs and verify the second run only processes new records from the bookmark
- Test load idempotency by running the same batch twice and asserting the target state is identical after both runs

### Failure Injection

- Crash the process mid-load and verify the bookmark was not advanced — next run reprocesses the incomplete batch
- Inject corrupt records in the extract phase and verify the pipeline logs errors without silently dropping data
- Simulate target database unavailability during load and confirm the pipeline retries or fails cleanly without advancing the bookmark

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

## Deployment

Job scheduling and bookmark state must be coordinated to avoid partial loads or duplicate processing.

### Rollout Implications

- Deploying new transform logic while a job is running may cause the in-flight job to produce inconsistent output — pause scheduling before rollout
- Bookmark/checkpoint format changes require migration — new code reading old bookmarks must handle the previous format
- Schema changes in the load target (new columns, type changes) must be applied before new ETL code deploys
- Parallel job execution during rollout can cause duplicate loads if both old and new versions process the same bookmark window

### Pre-deploy Checklist

- Verify no ETL jobs are currently running or scheduled to start during the deployment window
- Confirm bookmark/checkpoint state is compatible with the new code version
- Validate that target schema migrations are applied before deploying new transform or load logic

