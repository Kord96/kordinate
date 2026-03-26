---
description: Intermediate Representation (IR) architectural pattern
type: pattern
curated: true
scope: global
preloaded: none
---
# Intermediate Representation (IR)

## Recognition

How to identify this pattern in code.

### Signatures

- Lowered representation sitting between the AST (source) and final output (machine code, bytecode, target language)
- Static Single Assignment (SSA) form: each variable assigned exactly once, with phi nodes at control flow joins
- Basic blocks containing sequential instructions, connected by control flow edges
- IR passes: optimization, lowering, analysis passes that transform or inspect the IR
- `IRBuilder` or `emit()` methods constructing IR instructions from higher-level AST nodes
- Three-address code format: `result = op left right`
- Bytecode emission as a compact IR targeting a virtual machine
- Libraries/frameworks: LLVM IR, Cranelift, MLIR, WebAssembly, JVM bytecode, Python bytecode

### Confidence

- **high** — SSA-form instructions in basic blocks with optimization passes and an `IRBuilder` or `emit()` API
- **medium** — basic block graph with typed instructions, explicit control flow edges, and at least one transform pass
- **low** — flattened instruction list with opcodes emitted from an AST without structured basic blocks

## Architecture

Look for a structured intermediate form that enables optimization and analysis between parsing and code generation.

### Review Checklist

- IR is well-typed: every value and instruction carries a type, enabling type-based optimizations
- Basic blocks have a single entry point and single exit (branch/return), forming a proper CFG
- Optimization passes are composable and order-independent where possible (pass manager)
- IR-to-source mapping is preserved for debuggability (debug info, source locations)
- Lowering from AST to IR is a separate, testable phase (not interleaved with parsing)
- IR can be serialized and deserialized for caching, separate compilation, or debugging

### Anti-patterns

- AST used directly as the optimization target instead of lowering to a simpler IR first
- Optimization passes that mutate shared IR state without proper invalidation of analysis results
- No type system on the IR, allowing ill-typed instructions to reach code generation
- Monolithic lowering pass that converts AST to final output with no intermediate form
