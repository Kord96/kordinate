---
description: Request-Reply — testing guidance
type: supplementary
---
## Testing

Verify correlation ID matching, timeout behavior, and reply queue cleanup across the full request-reply lifecycle.

### Unit Tests

- Send a request and return a reply with the matching correlation ID; verify the requester receives the correct response
- Send a request and do not reply within the timeout; verify the requester receives a timeout error
- Send a request with a reply-to queue and verify the responder sends the reply to the specified queue
- Verify correlation ID uniqueness: generate many IDs and assert no collisions

### Integration Tests

- Run the full flow over a real broker (RabbitMQ, NATS) and verify end-to-end request-reply with correct correlation
- Verify temporary reply queues are deleted after the response is received or timeout fires
- Test idempotent responder: send the same request twice (same correlation ID) and verify the response is consistent
- Simulate responder restart mid-request and verify the requester times out cleanly (no hang)

### Failure Injection

- Kill the responder after it receives the request but before it sends the reply; verify the requester times out
- Introduce network latency exceeding the timeout and verify the requester handles the timeout without resource leak
