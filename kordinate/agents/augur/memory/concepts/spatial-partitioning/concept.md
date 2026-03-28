---
description: Spatial Partitioning architectural pattern
type: pattern
testable: true
curated: true
scope: global
preloaded: none
graphable: true
abstraction: [data, realtime]
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
