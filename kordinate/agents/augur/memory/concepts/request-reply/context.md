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

## Monitoring

Track correlation success rates, reply latencies, and timeout frequency to detect broken request-reply flows.

### Key Metrics

- `request_reply_sent_total` (counter) -- request messages sent, by destination
- `request_reply_received_total` (counter) -- reply messages received with matching correlation ID
- `request_reply_timeout_total` (counter) -- requests that timed out waiting for a reply
- `request_reply_latency_seconds` (histogram) -- round-trip time from request send to reply receipt
- `reply_queue_depth` (gauge) -- number of pending replies on temporary reply queues

### Alerts

- Timeout rate exceeds threshold (responder down, network issue, or reply queue misconfigured)
- Reply latency exceeds SLA for a sustained period (responder degraded or overloaded)
- Orphaned reply queues accumulating (queues not cleaned up after timeout or response)
- Correlation ID mismatch rate nonzero (reply routing broken, possible message interleaving)

## Deployment

Coordinate requester and responder lifecycle to avoid lost replies during rollouts.

### Rollout Implications

- Rolling restart of the requester may orphan reply queues on the broker -- ensure temporary queues have auto-delete or TTL
- Deploying the responder first is safer: new responder can handle both old and new request formats
- If requester and responder are co-deployed, stagger restarts to avoid both sides being unavailable simultaneously
- Timeout values must account for deployment-induced latency (briefly increased round-trip during pod replacement)

### Pre-deploy Checklist

- Verify the broker is healthy and reply queues are being created and cleaned up correctly
- Confirm correlation ID generation produces unique values (no collisions across requester instances)
- Check that timeout values on the requester side are appropriate for the responder's expected processing time
- Ensure temporary reply queues have TTL or auto-delete configured to prevent resource leaks on the broker

