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

- Classes named `*Composite` with a children collection delegating operations recursively to child components that share the same interface
- Explicit `CompositeItemProcessor`, `CompositeItemWriter`, `CompositeCommand` classes composing multiple implementations of the same interface
- Schema/rule composition: `allOf`, `anyOf`, `oneOf` combinators composing sub-schemas recursively
- Java: `CompositeItemProcessor`, `CompositeItemWriter` (Spring Batch) composing multiple processors/writers
- Java: abstract class with `List<SameInterface>` field and methods iterating children calling the same method

### Negative signals (not sufficient for detection)

- Generic tree data structures (e.g., `IdMap2`, `IdMap3`, nested Maps) or hierarchical data without a shared component interface are not composite
- The composite pattern requires a uniform interface across both individual elements and collections, enabling clients to treat single objects and compositions uniformly
- A tree-shaped data structure used for storage is not composite unless it has polymorphic operations
- The word `Composite` as a class name suffix alone is not sufficient -- look for the tree + shared interface + recursive delegation structure
- `children` or `child` as a field name in parent-child data relationships (e.g., database tree, organizational hierarchy) is data modeling, not the composite pattern

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
