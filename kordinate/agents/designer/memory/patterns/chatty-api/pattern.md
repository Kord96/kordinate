---
description: Chatty API anti-pattern
type: anti-pattern
curated: true
scope: global
preloaded: none
graphable: false
---
# Chatty API

## Recognition

How to identify this anti-pattern in code.

### Signatures

- Client making 10+ sequential API calls to assemble a single view or page
- No batch or bulk endpoints for operations that naturally apply to collections
- No GraphQL or aggregation layer despite clients needing data from multiple resources per screen
- N HTTP requests required to display N items (fetching details one by one)
- Frontend code orchestrating multiple backend calls and merging responses client-side

### Confidence

- **high** -- network tab or client code shows 10+ sequential requests to the same API for a single user action
- **medium** -- API provides only single-resource endpoints and the client loops over IDs to fetch related data
- **low** -- API lacks batch endpoints but current usage patterns fetch only a few items at a time

## Impact

Latency multiplies with each additional call, creating fragile client logic tightly coupled to backend resource structure.

### Symptoms

- Page load times are dominated by network round-trips rather than server processing
- Mobile clients suffer disproportionately due to higher per-request latency
- Client code contains complex orchestration logic to sequence, merge, and error-handle multiple API calls
- A single slow or failing backend call breaks the entire page because the client depends on all responses
- API rate limits are hit quickly because a single user action generates many requests

### Remediation

- Introduce batch/bulk endpoints that accept arrays of IDs and return aggregated results in one response
- Add a Backend-for-Frontend (BFF) layer that composes multiple service calls into a single client-facing response
- Consider GraphQL or a query-based API that lets clients request exactly the data they need in one round-trip
- Implement server-side view models or aggregation endpoints tailored to specific UI screens
- Combine related resources into composite responses with embedded or sideloaded associations
