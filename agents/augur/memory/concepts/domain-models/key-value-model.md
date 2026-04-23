---
kind: concept
name: key-value-model
signatures: {}
type: domain-model
abstraction:
- data
scope: domain
status: primary
family: domain-models
---

# Explanation

## Recognition

### Signatures

- Redis, Memcached, DynamoDB, etcd, or Consul as primary data store
- Data accessed exclusively by key — no complex queries or joins
- TTL/expiry on entries
- Cache patterns: get-or-set, cache-aside, write-through
- Session storage keyed by session ID
- Feature flags keyed by flag name
- Configuration storage keyed by config path
- Atomic operations: increment, compare-and-swap, SETNX

### Confidence

- **high** — key-value store as primary data model with TTL, atomic ops, and no relational queries
- **medium** — Redis/Memcached used as cache layer alongside a relational primary store
- **low** — dictionary/map data structures used extensively in code but no external KV store

### Relationship To Other Concepts

- Related to [cache-aside](/concepts/cache-aside) because many cache-aside designs rely on key-value access patterns and TTL semantics.
- Related to [read-through](/concepts/read-through) as another key-value-centric loading model where the store abstraction owns misses.
- Related to [lru-cache](/concepts/lru-cache) because many key-value systems pair direct lookup semantics with eviction and recency policies.

### Boundary

Use `key-value-model` when data is fundamentally organized and accessed as key-to-value lookup rather than by joins, graphs, or rich relational querying.

Do not use it for ordinary in-memory dictionaries or any system that merely contains some keyed tables.
