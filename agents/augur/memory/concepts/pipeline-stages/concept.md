---
description: Pipeline stages structure — components arranged as sequential processing stages
type: structure-shape
abstraction: [architectural, data]
---
# Pipeline Stages

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
