---
description: Select Star — monitoring guidance
type: supplementary
curated: true
scope: global
preloaded: none
---
# Monitoring

- Track query payload sizes — alert when response sizes are significantly larger than what the caller uses
- Monitor slow query logs for `SELECT *` patterns appearing in production query plans
- Alert on queries that bypass index-only scans due to requesting all columns
- Track database network I/O between application and database under load
- Monitor memory usage spikes correlated with large result set materialization
- Dashboard showing top-N widest queries (most columns fetched) alongside actual column usage
