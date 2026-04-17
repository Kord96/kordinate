---
description: Spatial Partitioning architectural pattern
type: pattern
testable: true
graphable: true
abstraction:
- data
- realtime
status: primary
scope: domain
relationships:
  related_to:
  - game-loop
  - tick-simulation
  - entity-component-system
aliases: []
disambiguates_from: []
preferred_over: []
implies: []
anti_signals: []
detector_coverage: partial
examples: []
---
# Spatial Partitioning

## Recognition

How to identify this pattern in code.

### Signatures

- Classes named `QuadTree`, `Octree`, `SpatialHash`, `RTree`, `BVH`, `Grid`
- `insert()`, `query()`, `remove()` methods taking spatial coordinates or bounding boxes
- Broad-phase collision detection separating cheap spatial queries from expensive narrow-phase checks
- Bounding volume hierarchies (`AABB`, `BoundingBox`, `BoundingSphere`)
- Neighbor queries: `query_radius()`, `query_rect()`, `nearest()`
- Recursive subdivision of space into cells or nodes with max capacity
- Libraries: libspatialindex, nanoflann, rbush (JS), scipy.spatial, boost.geometry

### Confidence

- **high** — `QuadTree`/`Octree`/`SpatialHash` class with insert and spatial query methods
- **medium** — grid-based bucketing of objects by position with neighbor lookups
- **low** — spatial coordinates used as hash keys or array indices for proximity checks

## Architecture

Look for a spatial data structure that accelerates range or proximity queries over positioned objects.

### Review Checklist

- Partition structure matches the dimensionality of the problem (2D: quadtree/grid, 3D: octree/BVH)
- Tree depth or cell size is bounded to prevent degenerate performance
- Objects that span multiple cells are handled correctly (overlap, insertion into multiple cells)
- Structure is rebuilt or updated incrementally as objects move
- Query interface returns candidates, not final results (broad-phase, not narrow-phase)
- Memory allocation strategy avoids per-frame heap churn (object pools, pre-allocated nodes)

### Anti-patterns

- Rebuilding the entire spatial structure every frame when incremental updates suffice
- Using a single flat list with O(n^2) pairwise distance checks instead of spatial queries
- Tree with no depth limit, causing stack overflow on clustered data
- Mixing broad-phase and narrow-phase logic in the same structure

### Relationship To Other Concepts

- Related to [game-loop](/concepts/game-loop) because spatial partitioning is often used to accelerate per-frame or per-tick neighborhood queries.
- Related to [tick-simulation](/concepts/tick-simulation) when partition indexes are updated alongside discrete simulation steps.
- Related to [entity-component-system](/concepts/entity-component-system) because ECS-based simulations often pair data-oriented entities with spatial partition structures for lookup efficiency.

### Boundary

Use `spatial-partitioning` when objects are organized into spatial indexes or regions to accelerate locality-based queries like collision, proximity, or visibility.

Do not use it for generic sharding, hashing, or any non-spatial partition of data.
