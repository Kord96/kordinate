---
description: Schema Registry architectural pattern
type: pattern
observable: true
distributed: true
graphable: true
abstraction:
- data
- integration
status: primary
scope: cross-cutting
relationships:
  related_to:
  - event-driven
  - schema-on-read
  - database-migration
aliases: []
disambiguates_from: []
preferred_over: []
implies: []
anti_signals: []
detector_coverage: none
examples: []
---
# Schema Registry

## Recognition

How to identify this pattern in code.

### Signatures

- Central registry for Avro, Protobuf, or JSON schemas with versioning and compatibility checks
- Producers and consumers retrieving or validating message schemas against a registry
- Subject/version naming conventions and compatibility policies
- Build or deploy gates enforcing backward or forward compatibility
- Runtime payloads carrying schema IDs or version references

### Confidence

- **high** -- one registry service or workflow manages message schema versions and compatibility for many producers and consumers
- **medium** -- schemas are centrally stored and reviewed, but compatibility checks are only partially automated
- **low** -- shared schema files exist in source control without a registry or governed compatibility process

## Architecture

Look for explicit governance of message or event contracts across independently evolving producers and consumers.

### Review Checklist

- Compatibility policy is defined and enforced
- Producers and consumers can evolve independently within documented guarantees
- Schema IDs or versions are traceable in runtime traffic
- Registry outages or mismatches have operational handling

### Anti-patterns

- Silent schema changes breaking downstream consumers
- One shared schema file edited ad hoc without compatibility checks
- Registry present but bypassed by hand-crafted payloads

### Relationship To Other Concepts

- Related to [event-driven](/concepts/event-driven) because schema registries commonly govern event contract evolution.
- Related to [schema-on-read](/concepts/schema-on-read) as a contrasting mode where payload structure is interpreted late and often inconsistently.
- Related to [database-migration](/concepts/database-migration) because both concern schema evolution, though one governs message contracts and the other live persistence state.

### Boundary

Use `schema-registry` when message schema evolution is centrally governed through versioned registration and compatibility controls.

Do not use it for ordinary shared DTO files. The key signal is registry-backed contract governance.
