---
description: Event log domain model — append-only log of events as source of truth
type: domain-model
abstraction: [data, messaging]
---
# Event Log

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
