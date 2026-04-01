---
description: Select Star — testing guidance
type: supplementary
---
# Testing

- Lint all raw SQL strings for `SELECT *` and flag any occurrence outside of ad-hoc/debug contexts
- Test that ORM queries use `.only()`, `.values()`, or `.defer()` by asserting the generated SQL
- Write integration tests comparing query plans with and without column projection to verify index usage
- Test repository methods to confirm they return DTOs or projections, not full entity objects for list endpoints
- Verify that adding a column to a table does not silently inflate existing query payloads
- Assert that NoSQL queries include projection parameters (`{field: 1}`) rather than returning full documents
- Run performance benchmarks comparing `SELECT *` vs explicit column queries on representative data volumes
