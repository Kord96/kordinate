---
description: Pagination architectural pattern
type: pattern
testable: true
curated: true
scope: global
preloaded: none
graphable: true
abstraction: [data, api]
---
# Pagination

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
- Helper functions: `pagination_builder`, `paginate()`, `build_pagination`, `get_paginated`
- Framework pagination: DRF `PageNumberPagination`, Flask `pagination_builder`, Spring `Pageable`/`Page<T>`

### Negative signals (not sufficient for detection)

- Internal use of `offset` in buffer/array indexing, byte offsets, or string parsing is not pagination
- SQL `LIMIT` in a migration or data cleanup script without API exposure is not pagination
- `pageSize` or `limit` in internal configuration (batch sizes, buffer limits) is not pagination

### Confidence

- **high** -- Cursor-based pagination with `pageInfo`/`has_next_page` or keyset pagination with stable ordering
- **medium** -- `limit`/`offset` parameters in API with total count and page metadata in response
- **low** -- SQL queries with `LIMIT` but no pagination metadata returned to the caller

## Architecture

Look for the right pagination strategy for the data size and access pattern, with stable ordering guarantees.

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
