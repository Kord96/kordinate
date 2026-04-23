---
kind: concept
name: pipeline-stages
signatures: {}
type: structure-shape
abstraction:
- architectural
- data
scope: cross-cutting
status: primary
family: structure-shapes
---

# Explanation

## Recognition

### Signatures

- Components named `Stage`, `Step`, `Phase`, `Processor` with sequential numbering or ordering
- Unix-pipe-style composition: output of stage N is input of stage N+1
- Compiler passes: lexer → parser → AST → optimizer → codegen
- Image processing: decode → resize → filter → encode
- CI/CD pipeline stages: build → test → deploy
- Middleware chains where each middleware processes and passes to next
- `Pipeline` class that composes `Stage` instances in order
- scikit-learn `Pipeline` with sequential transformers

### Confidence

- **high** — explicit pipeline class composing named stages with defined input/output contracts between stages
- **medium** — sequential function calls where each output feeds the next, but without formal pipeline structure
- **low** — code that processes data in steps but steps are not modular or reorderable

### Relationship To Other Concepts

- Related to [pipeline-filter](/concepts/pipeline-filter) because both decompose work into ordered transformation stages.
- Related to [data-pipeline](/concepts/data-pipeline) when the stages move or transform data through a larger processing flow.
- Related to [mapreduce](/concepts/mapreduce) as a specialized staged computation model with explicit distribution and reduction phases.

### Boundary

Use `pipeline-stages` when the system is organized as explicit sequential stages with well-defined handoffs between them.

Do not use it for any multi-step function where stages are not treated as real architectural units.
