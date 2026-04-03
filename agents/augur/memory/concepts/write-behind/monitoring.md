---
description: Write-Behind — monitoring guidance
---
## Monitoring

Track write buffer health, flush reliability, and cache-to-store consistency for the write-behind layer.

### Key Metrics

- `write_behind_buffer_depth` (gauge) — pending writes in the buffer, detects unbounded growth
- `write_behind_buffer_bytes` (gauge) — buffer memory usage, alerts before memory exhaustion
- `write_behind_flush_latency_seconds` (histogram) — time to flush buffered writes to the backing store
- `write_behind_flush_results_total` (counter) — flush outcomes partitioned by result (success, failure, partial)
- `write_behind_coalescing_ratio` (gauge) — writes received divided by writes flushed, measures batching effectiveness
- `write_behind_flush_retries_total` (counter) — retry attempts for failed flushes

### Alerts

- Buffer depth approaching configured memory limit (unbounded growth, potential OOM)
- Flush failure rate elevated (data loss risk if writes are not reaching the backing store)
- Cache-to-store drift detected during consistency check (stale or missing data in backing store)
- Flush retry count sustained (persistently failing backing store writes)
- Cache warm-up from backing store incomplete before accepting writes on startup
