---
description: Observer/Event Emitter architectural pattern
type: pattern
testable: true
graphable: true
abstraction:
- design
- messaging
status: primary
scope: cross-cutting
relationships:
  related_to:
  - pub-sub
  - event-driven
aliases: []
disambiguates_from: []
preferred_over: []
implies: []
anti_signals: []
detector_coverage: partial
examples: []
---
# Observer

## Recognition

How to identify this pattern in code.

### Signatures

- Methods named `subscribe()`, `on()`, `addListener()`, `register()`, `attach()`
- Emission methods: `emit()`, `notify()`, `publish()`, `dispatch()`, `fire()`
- Callback/handler registration with event names or types
- Python: `blinker` signals, `pyee.EventEmitter`, `asyncio` event patterns
- JS/TS: `EventEmitter`, `addEventListener`, RxJS `Observable.subscribe()`, custom event bus
- Go: channel-based pub/sub, callback slices
- Java: `java.util.Observer` (deprecated), Spring `ApplicationEvent`, Guava `EventBus`

### Confidence

- **high** -- explicit subscribe/emit pair with named events and registered handlers
- **medium** -- callback list maintained and iterated on state change
- **low** -- single callback parameter passed to a function (basic inversion of control)

## Architecture

Look for correct lifecycle management of subscriptions and defined event contracts.

### Review Checklist

- Subscriptions are cleaned up (unsubscribe on teardown to prevent memory leaks)
- Event contracts are defined (typed events, not arbitrary string keys with untyped payloads)
- Error in one observer does not prevent notification of remaining observers
- Ordering guarantees are documented (or explicitly unordered)
- No circular notification chains (observer A notifies B which notifies A)

### Anti-patterns

- Forgotten unsubscribe causing memory leaks or ghost handlers
- Observers mutating the event/subject during notification (action at a distance)
- String-based event names with no type safety on payloads
- Synchronous observer chain blocking the emitter when async would be appropriate

See also: pub-sub (inter-process variant)

### Relationship To Other Concepts

- Related to [pub-sub](/concepts/pub-sub) because both decouple producers from consumers, but observer is usually in-process and object-oriented.
- Related to [event-driven](/concepts/event-driven) when in-process events are part of a broader event-driven design.

### Boundary

Use `observer` when one in-process subject or emitter maintains listeners and notifies them on events or state changes.

Do not use it for broker-backed topic distribution, work queues, or ordinary callback parameters unless there is a clear observer registration model.
