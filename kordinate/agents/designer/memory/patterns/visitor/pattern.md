---
description: Visitor architectural pattern
type: pattern
curated: true
scope: global
preloaded: none
---
# Visitor

## Recognition

How to identify this pattern in code.

### Signatures

- `accept(visitor)` method on element/node classes
- `visit_*(node)` methods on visitor classes: `visit_BinaryExpr`, `visit_Literal`, `visit_IfStmt`
- Double dispatch: element calls `visitor.visit_X(self)` in its `accept()` method
- AST walkers, tree traversals, compiler passes, serialization visitors
- Python: `ast.NodeVisitor` with `visit_*` methods, `generic_visit()` fallback
- Java: `Visitor` interface with `visit()` overloads per element type
- Rust: visitor traits in `syn` crate, `Visit`/`VisitMut` patterns
- Go: `ast.Walk` with `ast.Visitor` interface

### Confidence

- **high** -- `accept(visitor)` on elements plus `visit_Type(element)` methods on visitors (classic double dispatch)
- **medium** -- visitor class with `visit_*` methods dispatched by element type, without explicit `accept()`
- **low** -- type-switch traversal over a union/enum of node types

## Architecture

Look for correct double dispatch and separation of algorithm from data structure.

### Review Checklist

- Each element type has an `accept()` that dispatches to the correct `visit_*` method
- Adding a new visitor does not require modifying element classes
- Visitor has access to the element's public interface, not its internals
- Traversal order is well-defined (depth-first, breadth-first) and controlled
- Fallback handling exists for unvisited element types (`generic_visit` or error)

### Anti-patterns

- Visitor reaching into element private state (breaks encapsulation)
- Adding a new element type requires modifying every existing visitor (fragile)
- Visitor accumulating mutable state across visits without clear reset boundaries
- Using visitor when a simple polymorphic method on the elements would suffice
