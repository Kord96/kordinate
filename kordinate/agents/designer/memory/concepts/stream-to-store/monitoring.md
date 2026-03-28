---
description: Stream-to-Store — monitoring guidance
curated: true
scope: global
preloaded: none
---
## Monitoring

Track consumer lag, buffer health, and store write performance to catch pipeline stalls early.

### Key Metrics

- `consumer_lag_records` (gauge) — records behind head per partition (Kafka consumer lag)
- `buffer_utilization_ratio` (gauge) — current buffer fill level as fraction of max capacity
- `flush_duration_seconds` (histogram) — time to flush buffer contents to the store
- `store_write_errors_total` (counter) — failed store write attempts
- `dead_letter_records_total` (counter) — messages sent to dead-letter queue

### Alerts

- Consumer lag exceeding threshold for a sustained period (pipeline falling behind)
- Buffer utilization above 80% (approaching memory exhaustion)
- Store write error rate spiking (downstream store degraded)
- Dead-letter queue depth growing without resolution
