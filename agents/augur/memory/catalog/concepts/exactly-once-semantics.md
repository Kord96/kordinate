---
description: Exactly-Once Semantics architectural pattern
type: pattern
observable: true
distributed: true
graphable: true
abstraction:
- messaging
- data
status: supporting
scope: cross-cutting
relationships:
  related_to:
  - at-least-once-delivery
  - idempotent-consumer
  - outbox
aliases: []
disambiguates_from: []
preferred_over: []
implies: []
anti_signals: []
detector_coverage: none
examples: []
---
# Exactly-Once Semantics

## Recognition

How to identify this pattern in code.

### Signatures

- Architecture claims one logical effect per input despite retries, crashes, or replay
- Transport, storage, and consumer behavior coordinated through transactions, idempotency, or deduplication
- Kafka transaction APIs, inbox/outbox pairing, or atomic write-plus-publish designs
- Strong emphasis on once-only business effect rather than literal single transport delivery

### Confidence

- **high** -- design explicitly distinguishes transport retries from one logical business effect and enforces that guarantee end to end
- **medium** -- infrastructure offers exactly-once features, but application correctness still depends on careful idempotency and atomicity
- **low** -- system advertises exactly-once based only on broker marketing or one local guarantee

## Architecture

Look for a deliberate end-to-end guarantee around one logical outcome, not naive faith in a transport feature.

### Review Checklist

- Guarantee is scoped precisely: transport, processing, or business effect
- Atomicity boundaries are explicit
- Recovery and replay behavior preserve once-only logical outcomes
- Operators can detect drift between claimed guarantee and actual failure behavior

### Anti-patterns

- Treating broker-level exactly-once as sufficient for end-to-end correctness
- Ignoring downstream side effects that are not covered by the guarantee
- Claiming exactly-once while retries can still duplicate business effects

### Relationship To Other Concepts

- Related to [at-least-once-delivery](/concepts/at-least-once-delivery) because many systems approximate exactly-once business outcomes on top of redelivering transports.
- Related to [idempotent-consumer](/concepts/idempotent-consumer) when duplicate-safe handling is part of the overall once-only effect.
- Related to [outbox](/concepts/outbox) when atomic publication and state change are used to narrow duplication windows.

### Boundary

Use `exactly-once-semantics` when the architecture explicitly pursues one logical effect per input across failure and retry conditions.

Do not use it for any durable queue. The important signal is an end-to-end semantic claim that must survive faults.
