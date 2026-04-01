---
description: Scatter-gather flow — request dispatched to multiple services, responses aggregated
type: flow-shape
abstraction: [integration]
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
