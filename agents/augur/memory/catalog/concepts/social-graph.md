---
description: Specialized graph application for user relationships and activity feeds
type: domain-model
category: domain-model
abstraction:
- data
- social
status: specialized
scope: domain
relationships:
  is_a:
  - graph
  related_to:
  - pub-sub
  - cache-aside
aliases: []
disambiguates_from: []
preferred_over: []
implies: []
anti_signals: []
detector_coverage: none
examples: []
---
# Social Graph

This is a social-network application of [graph](/concepts/graph), not a separate foundational graph family.

Use it when the code clearly models:
- follower/following or friend relationships
- timeline or feed fan-out
- mutual-connection or social-neighborhood traversal

## Recognition

How to identify this pattern in code.

### Signatures

- `follow`, `Follow`, `follower`, `following` models or table names
- `friend`, `Friend`, `connection`, `Connection` relationship models
- `feed`, `Feed`, `activity_stream`, `ActivityStream` for content distribution
- `timeline`, `Timeline` aggregation of followed users' activities
- `mutual` friends/followers computation queries
- Python: `django-activity-stream`, `stream-python`, `Follow` model with `follower` and `following` FK
- JS/TS: `getstream`, `@stream-io/node`, feed and follow API calls
- Go: `follow` table with `follower_id` and `following_id`, fan-out service
- Rust: social relationship structs, feed generation pipeline
- Java: `@ManyToMany` friend relationships, activity feed service

### Confidence

- **high** -- Follow/Connection model with fan-out feed generation, activity stream aggregation, and timeline queries across the social graph
- **medium** -- Follow table with follower/following relationships and basic feed queries joining followed users' posts
- **low** -- Simple user list or contact book without relationship-driven content distribution

## Architecture

### When to use
- Social platforms where users follow or connect with others and see their activity
- Community features in products (follow authors, subscribe to topics)
- Any system requiring relationship-driven content distribution and discovery

### Anti-patterns
- Computing feeds on read by joining all followed users' posts, which becomes O(n*m) and unscalable
- Symmetric friend relationships stored as a single row, making directional queries ambiguous
- No fan-out strategy, forcing timeline assembly at query time for every request

### Complements
- [graph](/concepts/graph) — primary graph concept in Augur
- [pub-sub](/concepts/pub-sub) — fan-out on write uses pub/sub to distribute activities
- [cache-aside](/concepts/cache-aside) — hot timelines benefit from cache-aside for feed caching

## Impact

Social graph operations (fan-out, timeline assembly, mutual friend computation) are among the most scale-sensitive patterns in application development. Feed generation strategy (fan-out on write vs. fan-out on read) is a fundamental architectural decision that affects latency, storage, and infrastructure costs.

### Relationship To Other Concepts

- Related to [pub-sub](/concepts/pub-sub) because this concept commonly appears alongside it or is clarified by contrast with it.
- Related to [cache-aside](/concepts/cache-aside) because this concept commonly appears alongside it or is clarified by contrast with it.
- A specialized form of [graph](/concepts/graph) with additional constraints or specialization.

### Boundary

Use `social-graph` when the important observation is this specific domain modeling concept within a domain-modeling or product-domain concern.

Do not promote it above a broader parent concept unless the specialization itself is what materially explains the design.
