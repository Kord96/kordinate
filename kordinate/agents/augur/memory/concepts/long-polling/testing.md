---
description: Long Polling — testing guidance
type: supplementary
---
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
