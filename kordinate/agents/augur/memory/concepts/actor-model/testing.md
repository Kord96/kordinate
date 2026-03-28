---
description: Actor Model — testing guidance
type: supplementary
curated: true
scope: global
preloaded: none
---
## Testing

Test actor behavior in isolation by sending messages and asserting responses, then verify supervision and concurrency.

### Unit Tests

- Send a message to an actor and assert the correct response or state change
- Verify that actors process messages sequentially — no concurrent state mutation
- Test supervision strategy: a failing child actor is restarted with correct initial state

### Integration Tests

- Wire multiple actors together and verify end-to-end message flow
- Test actor persistence: kill an actor, restart it, and verify state recovery from journal
- Verify dead letter handling for messages sent to stopped actors

### Failure Injection

- Inject exceptions in message handlers and verify the supervisor restarts the actor
- Flood an actor mailbox and verify backpressure or bounded-mailbox rejection behavior
