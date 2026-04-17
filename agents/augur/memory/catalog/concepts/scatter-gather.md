---
description: "Scatter-gather flow \u2014 request dispatched to multiple services,\
  \ responses aggregated"
type: flow-shape
abstraction:
- integration
status: primary
scope: cross-cutting
relationships:
  related_to:
  - request-reply
  - bff
  - fan-out
aliases: []
disambiguates_from: []
preferred_over: []
implies: []
anti_signals: []
detector_coverage: none
examples: []
---
# Scatter-Gather

## Recognition

### Signatures

- Parallel HTTP calls to multiple backends with results merged
- `Promise.all([serviceA.get(), serviceB.get(), serviceC.get()])`
- `asyncio.gather(fetch_prices(), fetch_inventory(), fetch_reviews())`
- Go `errgroup` dispatching concurrent requests to multiple services
- API gateway aggregating responses from multiple microservices
- Search federation: query sent to multiple indices, results ranked and merged
- Price comparison: same query to multiple providers, best result selected
- Timeout handling: return partial results if some services are slow
- GraphQL resolvers fetching from multiple data sources concurrently

### Confidence

- **high** — explicit parallel dispatch to N services with structured aggregation, timeout handling, and partial result support
- **medium** — parallel calls to multiple services but results merged ad-hoc without timeout or partial result handling
- **low** — sequential calls to multiple services that could be parallelized but aren't

### Relationship To Other Concepts

- Related to [request-reply](/concepts/request-reply) because scatter-gather usually fans requests out and then awaits multiple replies.
- Related to [bff](/concepts/bff) when one frontend-facing layer aggregates results from many downstream services.
- Related to [fan-out](/concepts/fan-out) because the request side of scatter-gather explicitly widens into parallel downstream calls.

### Boundary

Use `scatter-gather` when one logical request is intentionally dispatched to multiple downstream targets in parallel and later aggregated.

Do not use it for ordinary sequential aggregation. The defining property is parallel fan-out followed by coordinated gathering.
