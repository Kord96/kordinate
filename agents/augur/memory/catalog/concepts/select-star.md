---
description: Select Star anti-pattern
type: anti-pattern
testable: true
observable: true
graphable: false
status: supporting
scope: cross-cutting
relationships:
  related_to:
  - over-under-fetching
  - materialized-view
  - repository
aliases: []
disambiguates_from: []
preferred_over: []
implies: []
anti_signals: []
detector_coverage: partial
examples: []
---
# Select Star

## Recognition

How to identify this anti-pattern in code.

### Signatures

- `SELECT *` in production queries or raw SQL strings
- ORM loading full objects when only one or two fields are needed
- `Model.objects.all()` without `.values()`, `.only()`, or `.defer()`
- `findAll()` or `find({})` without a projection parameter
- Repository methods returning full entity objects for list/summary endpoints
- No column-level selection in query builders (`knex('table').select()` with no arguments)

### Confidence

- **high** -- `SELECT *` appears in a production query path confirmed by slow query logs or query plans showing full table scans with unnecessary columns
- **medium** -- ORM queryset fetches all fields and the consuming code only accesses 1-2 attributes, or `Model.objects.all()` is used without field restriction
- **low** -- repository method returns full model objects and callers serialize only a subset of fields

## Impact

Unnecessary data transfer over the wire, slower queries, and wasted application memory from materializing unused columns.

### Symptoms

- Query response payloads are significantly larger than what the caller actually uses
- Database I/O is higher than expected for the application's access patterns
- Memory usage spikes when loading large result sets with wide rows
- Network latency between application and database is elevated under load
- Index-only scans are not used because the query requests all columns

### Remediation

- Replace `SELECT *` with explicit column lists in all production queries
- Use `.only()`, `.values()`, or `.defer()` in ORM queries to fetch only needed fields
- Add projections to NoSQL queries (`find({}, {field1: 1, field2: 1})`)
- Create dedicated read models or DTOs for list/summary endpoints that only query required columns
- Add a query review step or linting rule that flags `SELECT *` outside of ad-hoc/debug contexts

### Relationship To Other Concepts

- Related to [over-under-fetching](/concepts/over-under-fetching) because `SELECT *` often reflects an API or read-path that pulls more data than the caller actually needs.
- Related to [materialized-view](/concepts/materialized-view) when dedicated read projections are introduced to avoid broad row fetches.
- Related to [repository](/concepts/repository) because repository or query-layer abstractions should usually centralize explicit field selection.

### Boundary

Use `select-star` when query paths fetch all columns by default even though only a subset is needed.

Do not use it for exploratory SQL, small tables, or cases where the full row is intentionally and consistently required.
