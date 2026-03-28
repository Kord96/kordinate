---
description: Composite architectural pattern
type: pattern
testable: true
curated: true
scope: global
preloaded: none
graphable: true
abstraction: [design]
---
# Composite

## Recognition

How to identify this pattern in code.

### Signatures

- Tree structures where leaf and composite nodes share the same interface (e.g., `Component` base with `Leaf` and `Container` subclasses)
- `children` list/collection on composite nodes with recursive operation delegation
- File system tree: files and directories implementing a common `FileSystemNode` interface
- UI widget trees: containers holding child widgets and delegating render/layout to all children
- Menu hierarchies with nested submenus sharing the same `MenuItem` interface
- Schema/rule composition: `allOf`, `anyOf`, `oneOf`, `not` combinators composing sub-schemas recursively

**Not this pattern:** Generic tree data structures (e.g., `IdMap2`, `IdMap3`, nested Maps) or hierarchical data without a shared component interface are not composite. The composite pattern requires a uniform interface across both individual elements and collections, enabling clients to treat single objects and compositions uniformly. A tree-shaped data structure used for storage is not composite unless it has polymorphic operations.

### Confidence

- **high** -- Shared interface with `children` collection on composite nodes and recursive operation delegation to children
- **medium** -- Tree structure with uniform operations on leaf and container nodes but without an explicit component interface
- **low** -- Nested data structures with recursive processing that resemble but do not formally implement the pattern

## Architecture

Look for a uniform interface applied to both individual objects and compositions, enabling recursive tree operations.

### Review Checklist

- Leaf and composite nodes implement the same interface consistently
- Add/remove child operations are only meaningful on composite nodes (not exposed on leaves, or safely no-op)
- Recursive operations have a clear base case at the leaf level
- Tree depth is bounded or guarded against stack overflow in recursive traversals
- Parent references, if present, are maintained consistently on add/remove

### Anti-patterns

- Leaf nodes exposing child-management methods that throw at runtime
- No depth limit on recursive operations, risking stack overflow on deep trees
- Type-checking nodes to determine leaf vs composite instead of relying on polymorphism
- Mutable shared state in the tree that causes unintended side effects during traversal
