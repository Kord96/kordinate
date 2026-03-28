---
description: Reactor/Event Loop — testing guidance
type: supplementary
curated: true
scope: global
preloaded: none
---
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
