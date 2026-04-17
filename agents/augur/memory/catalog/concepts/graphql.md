---
description: GraphQL architectural pattern
type: pattern
testable: true
observable: true
graphable: true
abstraction:
- api
- integration
status: primary
scope: backend
relationships:
  related_to:
  - pagination
  - rest
aliases: []
disambiguates_from: []
preferred_over: []
implies: []
anti_signals: []
detector_coverage: rich
examples: []
---
# GraphQL

## Recognition

How to identify this pattern in code.

### Signatures

- Schema definition language files with `type Query {}`, `type Mutation {}`, `type Subscription {}`
- Resolver functions mapping schema fields to data fetching logic
- Single endpoint (typically `/graphql`) handling all queries and mutations
- `.graphql` or `.gql` schema files
- Libraries: `graphene` (Python), `apollo-server` (Node), `strawberry` (Python), `graphql-java`, `gqlgen` (Go)
- Query strings with selection sets: `query { user(id: 1) { name email } }`
- DataLoader pattern for batching and caching nested field resolution

### Confidence

- **high** -- SDL schema files with resolvers, single `/graphql` endpoint, query/mutation type definitions
- **medium** -- GraphQL library imported with schema construction but mixed with REST endpoints
- **low** -- single endpoint accepting JSON queries but no formal GraphQL schema or SDL files

## Architecture

Look for a well-structured schema with efficient resolver implementation and proper query complexity controls.

### Relationship To Other Concepts

- `graphql` is the schema-driven query API concept: typed graph schema, resolvers, and selection sets.
- Use `pagination` for connection design and large collection traversal.
- Prefer `rest` when the system exposes stable resource endpoints rather than a graph query surface.

### Review Checklist

- Query depth and complexity limits are enforced to prevent abusive queries
- N+1 query problem is addressed with DataLoader or batching in resolvers
- Schema design follows a graph structure (connections between types) rather than mirroring REST resources
- Authentication and authorization are handled per-field or per-resolver, not just at the endpoint level
- Pagination uses cursor-based connections (Relay-style) for large collections
- Error handling follows GraphQL error specification with proper error extensions

### Anti-patterns

- No query depth or complexity limits (allows arbitrarily expensive queries)
- Resolvers making individual database calls per item without batching (N+1)
- Exposing database schema directly as GraphQL schema without an abstraction layer
- Using GraphQL for simple CRUD with no relationships (overhead without benefit)

### Boundary

Do not use `graphql` for any single `/graphql` endpoint wrapper. Prefer it only when schema-driven graph querying is materially shaping the architecture.

### Relationship To Other Concepts

- Related to [rest](/concepts/rest) as an alternative API style with different tradeoffs around resource modeling and client query flexibility.
- Related to [pagination](/concepts/pagination) because GraphQL collections often surface cursor-based connection patterns and query-shape-specific pagination concerns.
