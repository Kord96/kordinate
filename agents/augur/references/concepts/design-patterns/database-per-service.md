---
kind: concept
name: database-per-service
signatures: {}
source:
  memory_concept: memory/catalog/concepts/database-per-service.md
type: pattern
abstraction:
- data
- architectural
scope: cross-cutting
status: primary
---

# Explanation

## Recognition

How to identify this pattern in code.

### Signatures

- Each service owns its own database, schema, or persistence cluster
- Per-service migration history and credentials
- Cross-service communication via APIs or events instead of direct table access
- Distinct connection targets and data ownership boundaries per service
- Reporting or integration flows built from replication, events, or dedicated read models rather than shared writes

### Confidence

- **high** -- independently deployable services each own and migrate their own persistence boundary
- **medium** -- services use separate schemas in one shared instance, but ownership and access boundaries remain explicit
- **low** -- intended ownership exists in docs, but code still performs occasional cross-service reads or writes

## Architecture

Look for persistence boundaries aligned to service ownership rather than convenience joins across the system.

### Review Checklist

- One service owns schema evolution for each persistence boundary
- Cross-service data access happens through contracts, not direct database access
- Failure or migration in one service's store does not force coordinated changes elsewhere
- Reporting and analytics do not quietly become write-time integration paths

### Anti-patterns

- Shared writes across service boundaries
- Cross-service joins as normal production behavior
- One service's migration unexpectedly breaking another service

### Relationship To Other Concepts

- Related to [microservices](/concepts/microservices) because database-per-service is one common way to preserve autonomous service ownership.
- Related to [shared-database](/concepts/shared-database) as the main persistence-coupling alternative.
- Related to [bounded-context](/concepts/bounded-context) when persistence ownership follows context ownership.

### Boundary

Use `database-per-service` when persistence ownership is intentionally split along service boundaries.

Do not use it for any multi-schema system. The key signal is service-level ownership and isolation.
