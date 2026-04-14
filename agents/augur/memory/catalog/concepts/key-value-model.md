---
description: Key-value domain model — simple key→value lookups with optional expiry
type: domain-model
abstraction: [data]
---
# Key-Value

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
