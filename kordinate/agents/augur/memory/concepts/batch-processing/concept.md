---
description: Batch processing flow — data processed in discrete chunks on a schedule
type: flow-shape
abstraction: [data, lifecycle]
---
# Batch Processing

## Recognition

### Signatures

- Cron-scheduled jobs processing accumulated data
- `LIMIT`/`OFFSET` or cursor-based pagination through a large dataset
- Batch size configuration: `BATCH_SIZE = 1000`
- Spring Batch `ItemReader` → `ItemProcessor` → `ItemWriter`
- Celery tasks with `chunks()` or batch processing
- DuckDB/Spark batch queries over partitioned data
- Nightly/hourly report generation
- Bulk API endpoints: `POST /api/bulk-import`
- Queue-based batch: accumulate N messages then process together
- `flush()` or `commit()` after processing a batch

### Confidence

- **high** — explicit batch framework or scheduled job with configurable batch size, progress tracking, and error handling per batch
- **medium** — periodic job processing accumulated data but without structured batching (processes all at once)
- **low** — large query results processed in a loop without explicit batch boundaries
