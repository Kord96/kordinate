---
description: Select Star — monitoring guidance
---
## Monitoring

Track query payload sizes and column usage to detect unnecessary data transfer from SELECT * patterns.

### Key Metrics

- `query_response_bytes` (histogram) — payload size per query path, surfaces oversized result sets
- `query_columns_fetched` (gauge) — number of columns returned per query versus columns actually consumed
- `query_slow_log_select_star_total` (counter) — SELECT * queries appearing in slow query logs
- `query_index_only_scan_bypass_total` (counter) — queries that miss index-only scans due to requesting all columns
- `db_network_io_bytes_total` (counter) — bytes transferred between application and database

### Alerts

- Query response payload significantly larger than the caller's actual column usage
- SELECT * pattern detected in production slow query logs
- Database network I/O elevated beyond expected baseline under normal load
- Memory usage spikes correlated with large result set materialization
