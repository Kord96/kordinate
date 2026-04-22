---
kind: concept
name: over-under-fetching
signatures: {}
source:
  memory_concept: memory/catalog/concepts/over-under-fetching.md
type: anti-pattern
abstraction: []
scope: backend
status: supporting
---

# Explanation

## Recognition

How to identify this anti-pattern in code.

### Signatures

- Returning entire database rows or full object graphs when the caller needs one or two fields (over-fetching)
- Multiple sequential API calls required to assemble the data for a single view (under-fetching)
- `/users` endpoint returning 50 fields when the UI displays 3
- `SELECT *` queries where only a few columns are used
- Client-side code filtering or reshaping API responses because the server returns too much or the wrong shape
- N+1 API call patterns: fetch a list, then fetch details for each item individually

### Confidence

- **high** -- an endpoint returns the full database model with 20+ fields and the primary consumer uses 3 of them, or a single page requires 5+ sequential API calls
- **medium** -- `SELECT *` is used in queries where a subset of columns would suffice
- **low** -- an endpoint returns a few extra fields beyond what the primary consumer needs (minor over-fetch)

## Impact

Wasted bandwidth, poor performance, and increased latency from either transferring unused data or making too many round-trips to assemble needed data.

### Symptoms

- API response payloads are disproportionately large relative to what the client renders
- Page load requires a waterfall of sequential API calls visible in the network tab
- Mobile clients consume excessive bandwidth and battery because of bloated responses
- Backend performance degrades under load because every request queries and serializes unnecessary data
- Clients maintain complex data-assembly logic that belongs on the server

### Remediation

- Design purpose-built endpoints or views that return exactly what each consumer needs (BFF pattern)
- Support field selection via query parameters (`?fields=id,name,email`) or GraphQL
- Replace N+1 API call patterns with batch endpoints or compound resources
- Use database projections: `SELECT id, name, email` instead of `SELECT *`
- Profile actual API usage to identify endpoints where response size and call count can be optimized

### Relationship To Other Concepts

- Related to [rest](/concepts/rest) because fixed endpoint shapes often trigger clients to over-fetch or under-fetch data they need.
- Related to [graphql](/concepts/graphql) because schema-driven field selection is often adopted specifically to reduce over- and under-fetching.
- Related to [bff](/concepts/bff) when tailored backend surfaces are introduced to better fit one client’s data needs.

### Boundary

Use `over-under-fetching` when an API shape systematically returns too much or too little data for its real consumers.

Do not use it for one expensive query or a single missing field request in isolation.
