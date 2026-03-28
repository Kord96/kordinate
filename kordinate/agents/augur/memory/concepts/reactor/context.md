## Testing

Verify non-blocking behavior, correct handler dispatch, and graceful shutdown under concurrent connections.

### Unit Tests

- Register a handler for an I/O event, trigger the event, and verify the handler is called with the correct payload
- Verify error in one handler does not prevent subsequent handlers from executing
- Test timeout handling: register a handler with a deadline and verify it fires or is cleaned up on expiry
- Assert no blocking calls exist on the event loop path (use loop debug mode or slow-callback detection)

### Concurrency Tests

- Open many concurrent connections and verify the event loop multiplexes them without spawning a thread per connection
- Verify backpressure: when a write buffer fills, the loop pauses reads from the producer until the buffer drains
- Test graceful shutdown: signal the loop to stop and verify all in-flight events are drained before exit

### Integration Tests

- Run the reactor under load with real I/O (sockets, file descriptors) and verify no event starvation or deadlock
- Offload a CPU-bound task to the thread pool and verify the event loop remains responsive during computation
- Simulate a slow consumer and verify the loop applies backpressure rather than buffering unboundedly

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

