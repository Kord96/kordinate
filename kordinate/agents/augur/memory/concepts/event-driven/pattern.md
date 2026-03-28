---
description: Event-Driven architectural pattern
type: pattern
testable: true
observable: true
distributed: true
curated: true
scope: global
preloaded: none
graphable: true
abstraction: [architectural, messaging]
---
# Event-Driven Architecture

## Recognition

How to identify this pattern in code.

### Signatures

- Domain events as first-class objects with type, timestamp, and payload
- Event bus or event dispatcher: `emit_event()`, `publish_event()`, `dispatch()`
- Event handler registration: `@event_handler`, `on_event()`, `subscribe(EventType, handler)`
- Event store for persisting events (distinct from event sourcing if no replay)
- Event classes: `OrderCreated`, `UserRegistered`, `PaymentProcessed`
- `events/` directory containing event definitions and handlers
- Event metadata: event ID, timestamp, source, correlation ID

### Confidence

- **high** -- domain events published through an event bus with registered handlers reacting to typed events
- **medium** -- service emits events to a message broker and downstream services consume them
- **low** -- callback hooks or observer pattern used for loose coupling without explicit event objects

## Architecture

Look for components communicating through well-defined domain events rather than direct method calls, with producers decoupled from consumers.

### Review Checklist

- Events are immutable and carry all data needed for handlers to act (no callbacks to the source)
- Event schema is versioned to allow independent evolution of producers and consumers
- Handler failures do not prevent other handlers from processing the same event
- Event ordering is preserved where business logic requires it
- Idempotent handlers tolerate duplicate event delivery

### Anti-patterns

- Events used as remote procedure calls (event payload is a command, not a fact)
- Circular event chains where event A triggers B which triggers A
- Handlers that query back to the producer for additional data (tight coupling disguised as events)
- No event schema registry, leading to silent contract breakage between services

See also: event-notification (thin events), event-carried-state (fat events)
