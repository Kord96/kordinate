---
description: Event-Driven architectural pattern
type: pattern
testable: true
observable: true
distributed: true
graphable: true
abstraction:
- architectural
- messaging
status: primary
scope: cross-cutting
relationships:
  related_to:
  - pub-sub
  - choreography
  - event-sourcing
aliases: []
disambiguates_from: []
preferred_over: []
implies: []
anti_signals: []
detector_coverage: none
examples: []
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

### Payload Variants

Treat these as event payload design choices within an event-driven system, not separate top-level architecture families:

- thin events / notification-first payloads
- fat events / event-carried state transfer

Use `pub-sub` separately when the delivery mechanism itself matters.

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

See also: `pub-sub` for topic fan-out delivery semantics

### Relationship To Other Concepts

- Related to [pub-sub](/concepts/pub-sub) when events are distributed through topics or channels with fan-out semantics.
- Related to [choreography](/concepts/choreography) when event reactions across services collectively drive multi-step behavior without a central controller.
- Related to [event-sourcing](/concepts/event-sourcing) when events are not only communication artifacts but also the authoritative persistence model.

### Boundary

Use `event-driven` when facts or state changes are communicated primarily through events and downstream behavior is organized around reacting to them.

Do not use it for any system that emits notifications. The important signal is that event flow materially shapes the architecture.
