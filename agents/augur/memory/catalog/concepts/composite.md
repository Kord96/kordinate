---
description: Composite architectural pattern
type: pattern
testable: true
graphable: true
abstraction: [design]
---
# Composite

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
