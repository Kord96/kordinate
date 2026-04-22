---
kind: concept
name: composite
signatures: {}
source:
  memory_concept: memory/catalog/concepts/composite.md
type: pattern
abstraction:
- design
scope: backend
status: primary
---

# Explanation

## Recognition

How to identify this pattern in code.

### Signatures

- Tree structures where leaves and containers share the same interface
- `children` list or collection on composite nodes
- Recursive `render()`, `execute()`, `accept()`, or `calculate()` methods
- File system tree implementations (files and directories as same type)
- UI widget trees (containers holding other widgets)
- Menu hierarchies with nested submenus
- `Component` base class/interface with `Leaf` and `Composite` subclasses

### Confidence

- **high** -- Shared interface with `children` collection on composite nodes and recursive operation delegation to children
- **medium** -- Tree structure with uniform operations on nodes but without an explicit component interface
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

### Relationship To Other Concepts

- Related to [component](/concepts/component) when UI or domain trees are structured so leaf and container nodes share one abstraction.
- Related to [graph](/concepts/graph) as a contrast: composite is specifically about uniform treatment of hierarchical parent-child structures rather than general graph connectivity.
- Related to [visitor](/concepts/visitor) when operations need to traverse composite structures without bloating node interfaces.

### Boundary

Use `composite` when leaves and containers are intentionally exposed through one common interface so clients can treat a hierarchy uniformly.

Do not use it for any tree or nested structure. The important signal is uniform treatment of both single objects and composed groups.
