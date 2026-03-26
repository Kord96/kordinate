---
description: ETL — testing guidance
curated: true
scope: global
preloaded: none
---
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
