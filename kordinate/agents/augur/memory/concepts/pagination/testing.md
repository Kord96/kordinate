---
description: Pagination — testing guidance
type: supplementary
curated: true
scope: global
preloaded: none
---
## Testing

Verify correct page boundaries, stable ordering, and completeness when iterating through all pages.

### Unit Tests

- Request the first page and verify the correct number of items and valid next-page cursor or link
- Iterate through all pages and verify every record appears exactly once with no duplicates or gaps
- Request a page size of zero or negative and verify the API returns a validation error, not an unbounded result set
- Test boundary: dataset size is an exact multiple of page size (last page is full, no phantom next page)

### Cursor/Keyset Tests

- Insert a new record mid-iteration and verify cursor-based pagination does not skip or duplicate existing records
- Delete a record mid-iteration and verify the next page still returns correct results
- Submit an invalid or tampered cursor and verify the API rejects it with a clear error

### Integration Tests

- Verify database queries use indexed columns for the sort key (check query plan for seq scans on deep pages)
- Test offset-based pagination at high offsets and confirm performance degrades predictably (document the limit)
- Verify pagination metadata (total_count, has_next_page) is accurate after concurrent inserts and deletes
