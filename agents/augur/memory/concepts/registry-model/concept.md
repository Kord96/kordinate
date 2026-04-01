---
description: Registry domain model — entities with lifecycle states, metadata, and lookups
type: domain-model
abstraction: [data]
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
