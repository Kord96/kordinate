## Testing

Verify correct hold-and-release behavior, timeout handling, and reconnection logic.

### Unit Tests

- Assert that the server holds the request open until data is available, then responds immediately
- Verify that requests time out and return a proper response (not an error) when no data arrives within the timeout window
- Test that the client re-requests immediately after receiving a response or timeout

### Integration Tests

- Push data to the server while a long-poll request is held and verify the client receives it promptly
- Simulate server unavailability and verify the client backs off on errors instead of flooding with retries
- Test concurrent long-poll connections from multiple clients and confirm each receives its own data

### Edge Cases

- Disconnect the client mid-hold and verify the server cleans up the abandoned connection
- Send data just as the timeout fires and verify no race condition causes data loss or duplicate delivery

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

