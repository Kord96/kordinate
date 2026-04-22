---
kind: concept
name: pagination
signatures:
  concept: pagination
  positive:
    strong:
    - explicit page, cursor, or connection contracts with metadata
    - stable ordering and bounded page-size behavior
    medium:
    - limit and offset usage visible in API or query builders
    weak:
    - slices or limits with no outward pagination contract
  negative:
  - unbounded list endpoints with no page controls
  - incidental query limits misread as a pagination design
  notes:
  - Pagination is an API and data-access concept, not just a SQL optimization detail.
source:
  memory_concept: memory/catalog/concepts/pagination.md
type: pattern
abstraction:
- data
- api
scope: cross-cutting
status: primary
review_questions:
  threshold: 5
  entries:
  - id: pagination-client-contract
    prompt: Does the API expose a stable paging contract such as cursor, page, or
      limit plus metadata?
    weight: 3
    signals:
    - limit
    - offset
    - cursor
  - id: pagination-stable-ordering
    prompt: Is pagination grounded in a stable ordering or cursor strategy rather
      than ad-hoc slicing?
    weight: 2
    signals:
    - take
    - skip
    - pageInfo
monitoring:
  applies_to:
  - flow
  health_signals:
  - name: pagination.deep_page.latency
    description: Latency for requests that traverse many pages or use deep offsets.
  business_metrics: []
  gaps:
  - Missing deep-page latency visibility hides offset-pagination scalability problems.
---

# Explanation

## Recognition

How to identify this pattern in code.

### Signatures

- `limit`/`offset` query parameters or `LIMIT ? OFFSET ?` in SQL queries
- Cursor-based pagination with `next_cursor`, `after`, `before` parameters
- `page`/`per_page` or `page`/`page_size` request parameters
- `Link` response header with `rel=next`, `rel=prev`, `rel=first`, `rel=last`
- `has_more`, `has_next_page` boolean flag in response payloads
- Keyset pagination using `WHERE id > ? ORDER BY id LIMIT ?`
- `totalCount`, `pageInfo`, `edges`/`nodes` in GraphQL connection pattern (Relay spec)

### Confidence

- **high** -- Cursor-based pagination with `pageInfo`/`has_next_page` or keyset pagination with stable ordering
- **medium** -- `limit`/`offset` parameters in API with total count and page metadata in response
- **low** -- SQL queries with `LIMIT` but no pagination metadata returned to the caller

## Architecture

Look for the right pagination strategy for the data size and access pattern, with stable ordering guarantees.

### Relationship To Other Concepts

- `pagination` is the traversal contract for large result sets.
- It commonly appears inside `rest`, `graphql`, and `search-index` flows.
- Prefer those concepts when the main concern is the API style or search subsystem rather than result slicing mechanics.

### Review Checklist

- Pagination strategy matches the use case: offset for small datasets, cursor/keyset for large or real-time data
- Results are ordered by a stable, unique key to prevent duplicates and missed records across pages
- Response includes pagination metadata (total count or has_more flag, next cursor or page link)
- Default and maximum page sizes are enforced to prevent clients requesting unbounded result sets
- Cursor values are opaque to clients and resistant to tampering (base64-encoded, signed, or encrypted)
- Database queries use appropriate indexes to support the pagination ordering efficiently

### Anti-patterns

- Using `OFFSET` on large datasets where deep pages cause full table scans (offset 100000)
- No stable sort order, causing records to shift between pages as data changes
- Exposing raw database IDs or internal state as cursor values that clients can manipulate
- Missing maximum page size limit, allowing a single request to fetch the entire dataset

### Boundary

Do not use `pagination` for every endpoint with `limit`. Prefer it when result-windowing strategy, cursor design, or stable traversal are meaningful architectural choices.
