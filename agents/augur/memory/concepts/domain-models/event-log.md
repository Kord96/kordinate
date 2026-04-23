---
kind: concept
name: event-log
signatures: {}
type: domain-model
abstraction:
- data
- messaging
scope: cross-cutting
status: primary
family: domain-models
---

# Explanation

## Recognition

### Signatures

- Append-only tables or streams — inserts only, no updates or deletes
- Event tables with `event_type`, `payload`, `timestamp`, `sequence_number`
- Kafka topics, Kinesis streams, or Pulsar topics as primary data store
- Event replay capability — can rebuild state from events
- Schema registry for event versioning (Avro, Protobuf schemas)
- Snapshotting to avoid replaying entire history
- Event upcasting/versioning for schema evolution
- Audit log tables that record every state change

### Confidence

- **high** — append-only event store with replay capability, schema versioning, and snapshotting
- **medium** — append-only audit tables with event types but no replay or schema versioning
- **low** — log tables that record changes but are treated as secondary data, not source of truth

### Relationship To Other Concepts

- Related to [event-sourcing](/concepts/event-sourcing) because event logs are often the storage medium event-sourced systems replay from.
- Related to [audit-logging](/concepts/audit-logging) because both preserve historical events, though audit logs emphasize accountability rather than replay-driven state reconstruction.
- Related to [ledger](/concepts/ledger) when append-only event history is treated as durable authoritative record.

### Boundary

Use `event-log` when an append-only sequence of events itself is an important domain or storage concept, whether or not the full system is event sourced.

Do not use it for any logging stream. The key signal is a meaningful append-only event record, not diagnostics alone.
