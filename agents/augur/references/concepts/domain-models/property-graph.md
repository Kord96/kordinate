---
kind: concept
name: property-graph
signatures: {}
source:
  memory_concept: memory/catalog/concepts/property-graph.md
type: domain-model
abstraction:
- data
- graph
scope: domain
status: specialized
---

# Explanation

This is a specialized variant of [graph](/concepts/graph), not a separate top-level graph family.

Use it when the code clearly models:
- typed nodes and edges
- attributed relationships
- multi-hop traversal or graph query APIs

If the code only needs a general dependency graph, DAG, or traversal structure, prefer `graph`.

## Recognition

How to identify this pattern in code.

### Signatures

- `Node` and `Edge` or `Vertex` and `Relationship` class definitions with property maps
- Neo4j driver imports (`neo4j`, `py2neo`) or Cypher query strings (`MATCH (n)-[r]->(m)`)
- Gremlin traversal API: `g.V()`, `g.E()`, `addV()`, `addE()`, `has()`, `out()`, `in()`
- Python: `networkx.Graph`, `networkx.DiGraph` with `node[attr]` and `edge[attr]` access
- JS/TS: `neo4j-driver` package, `session.run('MATCH ...')` calls
- Go: `neo4j-go-driver`, custom `Node` and `Edge` structs with `Properties map[string]interface{}`
- Rust: `petgraph` with `NodeWeight` and `EdgeWeight` generics
- Java: `org.neo4j.driver`, TinkerPop `Graph` and `Traversal` interfaces
- `adjacency` list or matrix representations with per-node/per-edge metadata

### Confidence

- **high** -- Neo4j/Gremlin client with Cypher or Gremlin traversal queries, or Node/Edge classes with typed properties and relationship types
- **medium** -- networkx or petgraph usage with attributed nodes and edges for domain modeling
- **low** -- Adjacency list with basic metadata but no explicit graph schema or typed relationships

## Architecture

### When to use
- Domains with rich, many-to-many relationships where traversal depth matters (knowledge graphs, social networks, fraud detection)
- When query patterns involve multi-hop traversals, shortest paths, or pattern matching across relationships
- Schema-flexible environments where new relationship types emerge frequently

### Anti-patterns
- Using a property graph for simple tabular data that would be better served by a relational model
- Unbounded traversals without depth limits, causing query timeouts on large graphs
- Treating the graph as a document store by cramming all data into node properties instead of modeling relationships

### Complements
- [graph](/concepts/graph) — primary graph concept in Augur
- [search-index](/concepts/search-index) — graph data often needs full-text search over node properties

## Impact

A property graph model fundamentally shapes query patterns and performance characteristics. Traversal-heavy workloads scale differently than relational joins, requiring specialized indexing, query profiling, and capacity planning around graph density and traversal depth.

### Relationship To Other Concepts

- Related to [search-index](/concepts/search-index) because this concept commonly appears alongside it or is clarified by contrast with it.
- A specialized form of [graph](/concepts/graph) with additional constraints or specialization.

### Boundary

Use `property-graph` when the important observation is this specific domain modeling concept within a domain-modeling or product-domain concern.

Do not promote it above a broader parent concept unless the specialization itself is what materially explains the design.
