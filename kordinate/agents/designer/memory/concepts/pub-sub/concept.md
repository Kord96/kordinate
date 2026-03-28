---
description: Publish-Subscribe architectural pattern
type: pattern
testable: true
observable: true
distributed: true
curated: true
scope: global
preloaded: none
graphable: true
abstraction: [messaging, integration]
---
# Publish-Subscribe

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
