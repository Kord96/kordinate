---
description: "Registry domain model \u2014 entities with lifecycle states, metadata,\
  \ and lookups"
type: domain-model
abstraction:
- data
status: primary
scope: domain
relationships:
  related_to:
  - catalog
  - workflow-state-machine
  - soft-delete
aliases: []
disambiguates_from: []
preferred_over: []
implies: []
anti_signals: []
detector_coverage: none
examples: []
---
# Registry

## Recognition

### Signatures

- Entity classes with `status`/`state` fields and defined lifecycle transitions
- CRUD operations as the primary API surface
- Unique identifiers (UUID, slug, email) used for lookups
- Metadata/tags/labels attached to entities
- Soft delete (status=archived/deleted) rather than hard delete
- Search/filter by multiple fields
- Audit fields (created_at, updated_at, created_by)
- Entity relationships: one-to-many, many-to-many via join tables
- CRM-like patterns: contacts → companies → interactions

### Confidence

- **high** — entities with explicit lifecycle states, CRUD API, unique identifiers, and audit trail
- **medium** — standard CRUD with status fields but no defined state machine
- **low** — simple database tables with basic CRUD but no lifecycle or metadata patterns

### Relationship To Other Concepts

- Related to [catalog](/concepts/catalog) because both organize identifiable records with lookup surfaces, though registries usually emphasize lifecycle and operational metadata.
- Related to [workflow-state-machine](/concepts/workflow-state-machine) when registered entities move through explicit lifecycle states.
- Related to [soft-delete](/concepts/soft-delete) because registries often preserve deactivated records rather than physically deleting them.

### Boundary

Use `registry-model` when the core domain centers on identifiable records with metadata, lifecycle state, and lookup or administration operations.

Do not use it for every CRUD table or any collection of records without a meaningful lifecycle or registry semantics.
