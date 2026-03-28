---
description: GraphQL architectural pattern
type: pattern
testable: true
observable: true
curated: true
scope: global
preloaded: none
graphable: true
abstraction: [api, integration]
---
# GraphQL

## Recognition

How to identify this pattern in code.

### Signatures

- Schema definition language files (`.graphql`, `.gql`) with `type Query {}`, `type Mutation {}`, `type Subscription {}`
- Resolver functions mapping schema fields to data fetching logic
- Single endpoint (typically `/graphql`) handling all queries and mutations
- Libraries: `graphene` (Python), `apollo-server`/`@apollo/server` (Node), `strawberry` (Python), `graphql-java`, `gqlgen` (Go), `type-graphql` (TS)
- `buildSchema()`, `makeExecutableSchema()`, `typeDefs`, `resolvers` configuration
- Query strings with selection sets: `query { user(id: 1) { name email } }`

**Not this pattern:** The word "query" alone does not indicate GraphQL. SQL query builders, database query methods, or any API that accepts query parameters are not GraphQL. Look for the specific GraphQL SDL schema format, GraphQL library imports, or the `/graphql` endpoint.

### Confidence

- **high** -- SDL schema files (`.graphql`/`.gql`) with resolvers, single `/graphql` endpoint, query/mutation type definitions
- **medium** -- GraphQL library imported (`graphql`, `apollo-server`, `type-graphql`) with schema construction
- **low** -- schema-driven API with selection sets but using a non-standard GraphQL implementation

## Architecture

Look for a well-structured schema with efficient resolver implementation and proper query complexity controls.

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
