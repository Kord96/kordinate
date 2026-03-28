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
- Libraries: Redis Pub/Sub (`redis.subscribe`, `redis.publish`), NATS subjects, Google Pub/Sub, AWS SNS, MQTT
- `PubSub` class or module implementing publish/subscribe lifecycle
- Subscription management: subscribe, unsubscribe, subscription filters
- Java: Kafka `@KafkaListener` annotations consuming from topics, `KafkaTemplate.send(topic, message)` publishing
- Java: Spring `ApplicationEventPublisher` with `@EventListener` for in-app pub-sub
- Java: JMS `TopicSubscriber`, `TopicPublisher` for JMS topic-based messaging
- Go: NATS `nc.Subscribe(subject, handler)` and `nc.Publish(subject, data)` patterns
- Go: Redis pub/sub via `go-redis` `Subscribe()` / `Publish()` methods
- Any language: Kafka producer/consumer with topic-based routing (detect via `KafkaProducer`, `KafkaConsumer`, `KafkaTemplate`, `sarama`, `confluent-kafka`)

**Not this pattern:** EventEmitter `on()`/`emit()` within a single process is the observer pattern, not pub-sub. Pub-sub requires a message broker or bus that decouples publishers from subscribers -- they do not have direct references to each other. In-process callbacks are observers. Python: `publish` or `subscribe` as method names on domain objects (e.g., "publish a blog post", "subscribe a user to a newsletter") are domain verbs, not the pub-sub messaging pattern. Only flag when there is a messaging broker (Redis, NATS, Kafka) or an event bus class mediating between publishers and subscribers.

### Confidence

- **high** -- explicit topic-based publish with multiple independent subscribers via a message broker (Redis, NATS, Kafka, SNS)
- **medium** -- application-level event bus with named topics and decoupled publishers/subscribers
- **low** -- broadcast mechanism where components receive notifications but routing is through a central dispatcher

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
