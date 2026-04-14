---
description: Thin-event payload variant within event-driven architecture
type: flow-shape
testable: true
distributed: true
abstraction: [messaging, integration]
status: specialized
scope: cross-cutting
relationships:
  part_of: [event-driven]
---
# Event Notification (Thin Events)

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
