---
kind: concept
name: fan-out
signatures: {}
type: flow-shape
abstraction:
- messaging
- integration
scope: cross-cutting
status: primary
family: flow-shapes
---

# Explanation

## Recognition

### Signatures

- One Kafka/RabbitMQ/SNS producer with multiple consumer groups on the same topic
- Event emitter with multiple listeners: `emitter.on('user_created', handler1, handler2)`
- Pub/sub topic with multiple subscriptions
- `Promise.all()` or `asyncio.gather()` dispatching parallel work
- Webhook dispatcher sending the same event to multiple registered URLs
- CDC (Change Data Capture) feeding multiple downstream systems
- SNS → multiple SQS queues pattern
- One database trigger firing multiple downstream processes

### Confidence

- **high** — explicit pub/sub with multiple independent consumer groups processing the same event
- **medium** — one event handler dispatching to multiple functions sequentially (fan-out but not parallel)
- **low** — multiple modules importing the same event type but unclear if they process the same instance

### Relationship To Other Concepts

- Related to [pub-sub](/concepts/pub-sub) because publish-subscribe is one common mechanism for one-to-many fan-out.
- Related to [scatter-gather](/concepts/scatter-gather) because scatter phases often begin as fan-out before responses re-converge.
- Related to [webhook](/concepts/webhook) when one event source triggers multiple outbound callbacks.

### Boundary

Use `fan-out` when one upstream event, command, or stage intentionally branches work to many downstream paths.

Do not use it for simple loops or independent callers that happen to invoke the same service.
