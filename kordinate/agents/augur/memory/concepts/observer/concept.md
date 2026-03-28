---
description: Observer/Event Emitter architectural pattern
type: pattern
testable: true
curated: true
scope: global
preloaded: none
graphable: true
abstraction: [design, messaging]
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

**Not this pattern (Python):** `Signal()` from Django signals or `.on_\w+()` hooks alone do not confirm observer -- look for explicit subscribe/emit pairs with a list of registered handlers. A single `.connect()` call to a framework signal is framework usage, not an architectural pattern choice. Similarly, `.subscribe()` on an HTTP client or `.notify()` on a threading condition is not observer.

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
