---
kind: concept
name: pub-sub
signatures: {}
source:
  memory_concept: memory/catalog/concepts/pub-sub.md
type: pattern
abstraction:
- messaging
- integration
scope: cross-cutting
status: primary
---

# Explanation

## Recognition

How to identify this pattern in code.

### Signatures

- Topic or channel-based messaging: `publish(topic, message)`, `subscribe(topic, handler)`
- Fan-out delivery: all subscribers receive every message on a topic
- Topic declarations, channel names, or subject strings in configuration
- Libraries: Redis Pub/Sub, NATS subjects, Google Pub/Sub, AWS SNS, MQTT, Kafka topics
- Event emitters with `on(event_name, callback)` or `addEventListener` patterns
- Subscription management: subscribe, unsubscribe, subscription filters

### Confidence

- **high** -- explicit topic-based publish with multiple independent subscribers receiving every message
- **medium** -- event emitter pattern with named events and multiple listeners
- **low** -- broadcast mechanism where components receive notifications but routing is implicit

## Architecture

Look for decoupled producers and consumers communicating through named topics with fan-out delivery semantics.

### Relationship To Other Concepts

- `pub-sub` is the delivery topology: named topics and fan-out to multiple subscribers.
- Use `event-driven` when the main concern is fact-oriented domain communication rather than the broadcast mechanism.
- Use `websocket` when the important concern is long-lived client transport rather than brokered fan-out.

### Review Checklist

- Subscribers are idempotent (duplicate delivery is handled gracefully)
- Topic naming convention is consistent and documented
- Subscriber failures do not block other subscribers on the same topic
- Message ordering guarantees are understood and match requirements
- Backpressure handling exists for slow subscribers

### Anti-patterns

- Using pub/sub for point-to-point messaging where only one consumer should process each message
- Subscribers with side effects that break when receiving duplicate messages
- Topic explosion: creating a new topic per entity instead of using message filtering
- No monitoring of subscriber lag or dropped messages

See also: observer (in-process variant)

### Relationship To Other Concepts

- Related to [observer](/concepts/observer) because both decouple producers from consumers, but observer is usually in-process while pub-sub is commonly inter-process or broker-mediated.
- Related to [webhook](/concepts/webhook) when published events are delivered outward over registered HTTP callbacks.
- Related to [event-driven](/concepts/event-driven) because pub-sub is one common delivery style inside event-driven systems.

### Boundary

Do not use `pub-sub` for queues where only one consumer should receive a message. Prefer it only when fan-out semantics are the defining property.
