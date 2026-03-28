---
description: GraphQL — monitoring guidance
type: supplementary
curated: true
scope: global
preloaded: none
---
## Monitoring

Track query complexity, resolver performance, and error rates to prevent abuse and detect regressions.

### Key Metrics

- `graphql_query_duration_seconds` (histogram) — total query execution time, by operation name
- `graphql_resolver_duration_seconds` (histogram) — per-resolver execution time to identify slow fields
- `graphql_query_complexity` (histogram) — computed complexity score per query to detect expensive operations
- `graphql_errors_total` (counter) — resolver and validation errors, by error type and field path

### Alerts

- Query complexity exceeding the configured maximum (potential abuse or unoptimized client query)
- Resolver latency p99 spike for a specific field (backend regression behind that resolver)
- Error rate increase in a specific resolver (data source issue or schema mismatch)
