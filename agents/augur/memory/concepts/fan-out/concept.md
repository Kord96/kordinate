---
description: Fan-out flow — one event triggers parallel processing across multiple consumers
type: flow-shape
abstraction: [messaging, integration]
---
# Fan-Out

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
