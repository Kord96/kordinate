---
description: Shared Database architectural pattern
type: pattern
testable: true
graphable: true
abstraction:
- data
- integration
status: primary
scope: cross-cutting
relationships:
  related_to:
  - distributed-monolith
  - database-per-service
  - microservices
aliases: []
disambiguates_from: []
preferred_over: []
implies: []
anti_signals: []
detector_coverage: none
examples: []
---
# Shared Database

## Recognition

How to identify this pattern in code.

### Signatures

- Multiple services or components reading and writing the same schema or tables
- Independent applications configured with the same database credentials or connection targets
- Cross-service foreign keys or shared ORM models over one persistence boundary
- Schema migrations coordinated across nominally separate services
- Runtime coupling caused by one database acting as integration surface

### Confidence

- **high** -- multiple independently deployable services directly read or write the same tables or schema
- **medium** -- services share one database instance with partial schema ownership boundaries, but operational coupling remains
- **low** -- reporting or read-only access crosses boundaries without shared write ownership

## Architecture

Look for one persistence boundary coupling otherwise separate services or subsystems.

### Review Checklist

- Data ownership boundaries are explicit, not implicit
- Schema changes do not require coordinated releases across many services
- Shared reads are justified and controlled instead of becoming default integration
- Operational failures in one service cannot corrupt another service's persistence contract

### Anti-patterns

- Multiple services evolving the same tables without clear ownership
- Hidden coupling through shared ORM entities or migration scripts
- Treating the database as the primary integration API between services

### Relationship To Other Concepts

- Related to [distributed-monolith](/concepts/distributed-monolith) because shared persistence is one of the most common causes of distributed coupling.
- Related to [database-per-service](/concepts/database-per-service) as the main ownership-oriented alternative.
- Related to [microservices](/concepts/microservices) as a contrast: genuine service autonomy usually requires clearer persistence boundaries.

### Boundary

Use `shared-database` when multiple components or services intentionally couple through one database boundary.

Do not use it for ordinary reads from a reporting replica or warehouse. The important signal is shared operational ownership.
