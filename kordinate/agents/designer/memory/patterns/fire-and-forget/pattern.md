---
description: Fire and Forget anti-pattern
type: anti-pattern
observable: true
distributed: true
curated: true
scope: global
preloaded: none
---
# Fire and Forget

## Recognition

How to identify this anti-pattern in code.

### Signatures

- Publishing messages with no delivery guarantee or acknowledgment check
- `producer.send()` without awaiting acknowledgment or checking the returned future/promise
- No idempotency key on published messages
- No retry on publish failure (`try: send() except: pass`)
- `ignore_errors=True` or equivalent flag on message send calls
- No dead-letter queue or failure handling for undeliverable messages
- Async task dispatch (`celery.delay()`, `Task.Run()`) with no result tracking or error callback

### Confidence

- **high** -- message publish call has no error handling, no acknowledgment check, and no retry mechanism, confirmed by silent message loss visible in consumer-side gaps
- **medium** -- `producer.send()` is called without awaiting the result or registering an error callback, or `ignore_errors=True` is set on the send operation
- **low** -- messages are published without an idempotency key, or there is no dead-letter queue configured for the topic/queue

## Impact

Silent message loss leading to inconsistent state between services, with no visibility into what was lost.

### Symptoms

- Consumer-side counts do not match producer-side counts with no errors logged
- Downstream systems are missing data that should have been delivered via messages
- Intermittent data inconsistencies between services that are hard to reproduce
- No alerting fires when messages are lost because failures are silently swallowed
- Retry or reconciliation jobs are needed to fix state drift caused by lost messages

### Remediation

- Always await or check the acknowledgment/future returned by `producer.send()` and handle failures explicitly
- Implement the transactional outbox pattern: write messages to a database table in the same transaction as the business operation, then relay them to the broker
- Add idempotency keys to all published messages so consumers can safely handle duplicates from retries
- Configure dead-letter queues for all topics/queues and monitor them with alerts
- Add end-to-end message delivery monitoring that reconciles producer and consumer counts and alerts on divergence

See also: outbox pattern
