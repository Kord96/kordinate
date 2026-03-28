---
description: Reactor/Event Loop — monitoring guidance
type: supplementary
curated: true
scope: global
preloaded: none
---
## Monitoring

Track event loop health, callback latency, and blocking call detection to prevent throughput degradation.

### Key Metrics

- `event_loop_lag_seconds` (gauge) -- delay between scheduled callback time and actual execution time
- `event_loop_tasks_total` (counter) -- callbacks/handlers dispatched per second
- `event_loop_blocked_duration_seconds` (histogram) -- time spent in blocking calls detected on the event loop
- `active_connections` (gauge) -- number of concurrent connections multiplexed on the loop

### Alerts

- Event loop lag exceeds threshold (blocking call on the loop or CPU-bound work not offloaded)
- Active connection count approaching system file descriptor limit
- Task dispatch rate drops to zero while connections are active (event loop stalled)
- Blocked duration detected on the event loop (synchronous I/O or heavy computation inline)
