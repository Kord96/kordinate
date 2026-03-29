---
description: Abstract Syntax Tree (AST) architectural pattern
type: pattern
testable: true
graphable: true
abstraction: [data, compiler]
---
# Abstract Syntax Tree (AST)

## Recognition

How to identify this pattern in code.

### Signatures

- Tree node classes or enums representing language constructs (`IfExpr`, `BinOp`, `FnDecl`, `LetStmt`)
- Base type `ASTNode`, `Node`, or `Expr` with subtypes for each syntactic form
- `ExprNode`/`StmtNode`/`DeclNode` hierarchy separating expressions, statements, and declarations
- Visitor pattern: `visit_*` methods or `accept()` on nodes dispatching to a visitor
- Source location fields (`span`, `loc`, `pos`) on every node for error reporting and tooling
- Node type enum or tagged union discriminating between syntactic forms
- Tree traversal utilities: `walk()`, `traverse()`, `fold()` operating on the node tree

### Confidence

- **high** — node type hierarchy with `visit_*` methods, source location tracking, and distinct expression/statement/declaration categories
- **medium** — enum or tagged union of syntax node types with recursive children and span information
- **low** — nested data structures representing code with type tags but no formal visitor or traversal API

## Architecture

Look for a well-typed tree representation of parsed source code with systematic traversal support.

### Review Checklist

- Every node type carries source location for error messages, diagnostics, and source maps
- Node types are exhaustive: all language constructs have explicit representations (no catch-all "Other" node)
- Visitor or walker pattern enables traversal without modifying node definitions
- Tree is immutable after construction, with transformations producing new trees
- Type nodes distinguish expressions (produce values) from statements (produce effects)
- Pretty-printer can reconstruct source from AST, validating round-trip fidelity

### Anti-patterns

- Catch-all node type (e.g., `GenericNode`) used for multiple unrelated constructs
- Mutable AST nodes modified in place during analysis passes (hard to debug, prevents parallelism)
- No source location on nodes, making downstream error reporting impossible
- Visitor with default no-op methods that silently skip new node types after grammar changes
