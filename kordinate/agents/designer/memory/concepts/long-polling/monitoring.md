---
description: Long Polling — monitoring guidance
type: supplementary
curated: true
scope: global
preloaded: none
---
## Monitoring

Track connection lifecycle, timeout behavior, and server resource consumption from held requests.

### Key Metrics

- `long_poll_active_connections` (gauge) — number of currently held long-poll requests
- `long_poll_timeout_total` (counter) — requests that returned due to timeout with no new data
- `long_poll_data_returned_total` (counter) — requests that returned with data before timeout
- `long_poll_hold_duration_seconds` (histogram) — how long requests are held before responding

### Alerts

- Active connection count approaching server connection limit
- Timeout rate exceeding a threshold (clients waiting but no data arriving)
- Hold duration consistently hitting the maximum timeout (potential data delivery issue)
- Spike in reconnection rate (clients repeatedly failing and retrying)
