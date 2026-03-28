## Testing

Verify map and reduce function correctness independently, then test the full job on representative data.

### Unit Tests

- Test the map function with known inputs and assert the exact set of intermediate key-value pairs
- Test the reduce function with grouped intermediate values and assert the correct aggregated output
- Verify the reduce function is associative: `reduce(a, reduce(b, c)) == reduce(reduce(a, b), c)`

### Integration Tests

- Run the full job on a small, representative dataset and compare output against a golden reference
- Test with skewed data (one key having disproportionately many values) and verify correctness and completion
- Re-run the job on the same input and assert identical output (idempotency)

### Failure Injection

- Kill a mapper or reducer mid-task and verify the framework retries and completes the job correctly
- Introduce a poison record in the input and verify the job handles it gracefully (skip or dead-letter)

## Monitoring

Track job progress, task failures, and data skew to detect stalled or inefficient computations.

### Key Metrics

- `map_tasks_completed` / `reduce_tasks_completed` (counters) — progress through the job
- `task_failures_total` (counter) — map or reduce task failures requiring retry
- `shuffle_bytes_total` (counter) — intermediate data volume between map and reduce phases
- `partition_skew_ratio` (gauge) — ratio of largest to smallest partition size

### Alerts

- Job runtime exceeding expected duration (straggler tasks or data skew)
- Task failure rate above threshold (bad input data or resource exhaustion)
- Shuffle volume disproportionately large relative to input (inefficient map output or missing combiner)
- Single reducer receiving significantly more data than others (hot key skew)

## Deployment

Ensure cluster resources, data partitioning, and job configuration are correct before launching jobs.

### Rollout Implications

- New job versions should be tested on a subset of data before full-scale runs
- Resource allocation (mapper/reducer count, memory) must match the data volume of the target environment
- Updating the map or reduce logic requires reprocessing -- partial results from the old version are not compatible
- Intermediate data storage (shuffle space) must be sized for the expected shuffle volume

### Pre-deploy Checklist

- Verify input data paths exist and partitioning strategy is configured for the target cluster
- Confirm combiner is enabled where the reduce function is associative (reduces shuffle volume)
- Test that the job is idempotent: re-running produces identical output
- Validate resource limits (memory, CPU) prevent individual tasks from starving the cluster

