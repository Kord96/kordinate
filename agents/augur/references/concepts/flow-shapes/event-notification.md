---
kind: concept
name: event-notification
signatures: {}
source:
  memory_concept: memory/catalog/concepts/event-notification.md
type: flow-shape
abstraction:
- messaging
- integration
scope: cross-cutting
status: specialized
---

# Explanation

Treat this as a payload-design variant under [event-driven](/concepts/event-driven), not as a separate top-level event architecture family.

Use it when the important distinction is that events are intentionally thin and consumers fetch the full state later.

## Recognition

How to identify this pattern in code.

### Signatures

- Events containing only ID, type, and timestamp -- no entity payload
- Consumer must call back to the source service for full data
- Lightweight event bus or notification channel with minimal message size
- Event payloads like `{"type": "order.created", "id": "123", "timestamp": "..."}`
- Decoupled notification with consumer-initiated data fetch
- Contrast with event-carried state transfer where events contain full entity data

### Confidence

- **high** -- events explicitly carry only identifiers and consumers have a documented callback API to fetch full data
- **medium** -- small event payloads with IDs but unclear whether consumers are expected to call back or the data is just minimal
- **low** -- events are small but could simply be incomplete rather than intentionally thin

## Architecture

Look for notification-only events that trigger consumers to fetch data on demand from the source.

### Review Checklist

- Events are intentionally minimal -- ID, type, and timestamp only
- The source service exposes a stable API for consumers to fetch full entity data
- Consumers handle the case where the entity has changed between notification and fetch
- Event schema is versioned so consumers know what callback API to use
- The callback API can handle the load spike from many consumers fetching after a burst of events

### Anti-patterns

- Consumers making redundant callbacks for data they already have (no local caching)
- Source API not designed for the read amplification caused by thin events
- No versioning -- consumers break when the callback API changes
- Thin events used when consumers always need full data (unnecessary round trip)

### Relationship To Other Concepts

- Part of [event-driven](/concepts/event-driven) as one payload design choice within an event-driven system.
- Related to [event-carried-state](/concepts/event-carried-state) as the contrasting fat-event variant.
- Related to [webhook](/concepts/webhook) when notifications are delivered outward as minimal callback payloads that require later fetches.

### Boundary

Use `event-notification` when events are intentionally thin and consumers are expected to fetch more state from the source afterward.

Do not promote it to a top-level architecture family. It is a payload-shape distinction within event-driven systems, not a separate architectural style.
