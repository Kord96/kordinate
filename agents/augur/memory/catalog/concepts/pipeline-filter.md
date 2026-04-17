---
description: Pipeline/Filter architectural pattern
type: pattern
testable: true
graphable: true
abstraction:
- design
- data
status: primary
scope: backend
relationships:
  related_to:
  - data-pipeline
  - middleware
  - batch-processing
aliases: []
disambiguates_from: []
preferred_over: []
implies: []
anti_signals: []
detector_coverage: partial
examples: []
---
# Pipeline/Filter

## Recognition

How to identify this pattern in code.

### Signatures

- Ordered chain of transform functions where output of one feeds input of the next
- Pipe operators (`|>`, `|`, `>>`) composing stages
- Functions named `pipeline()`, `pipe()`, `compose()`, or `chain()`
- Filter chains with `addFilter()`, `addStage()`, or `addStep()`
- Data flowing through sequential stages in a defined order
- Unix-style composition: small single-purpose transforms piped together
- Functional pipeline libraries (`ramda`, `lodash/fp`, `transducers`)

### Confidence

- **high** -- Explicit `pipeline()` or `pipe()` call chaining multiple transform functions with typed stage interfaces
- **medium** -- Sequential function composition with data flowing left-to-right or top-to-bottom through stages
- **low** -- Array of functions applied in order, or a series of map/filter calls without a named pipeline abstraction

## Architecture

Look for each stage being a pure transform with a uniform interface and no coupling between non-adjacent stages.

### Review Checklist

- Each filter/stage has a uniform interface (same input/output shape or a common protocol)
- Stages are independently testable -- no hidden state shared between stages
- Pipeline order is explicit and configurable, not hardcoded in scattered locations
- Error handling is defined per-stage or at the pipeline level, not silently swallowed mid-chain
- Stages are reusable across different pipelines without modification
- Back-pressure or buffering strategy exists when stages have different throughput rates

### Anti-patterns

- Stages that reach into other stages' internal state instead of communicating through the pipe
- Monolithic transform that does everything in one function disguised as a "pipeline"
- No error propagation -- a failing stage silently passes corrupt data downstream
- Tightly coupled stage ordering where inserting or removing a stage breaks the chain

### Relationship To Other Concepts

- Related to [data-pipeline](/concepts/data-pipeline) because many data pipelines are concrete pipeline/filter systems over staged transforms.
- Related to [middleware](/concepts/middleware) when request processing is modeled as a filter chain around a handler.
- Related to [batch-processing](/concepts/batch-processing) when filters operate over discrete chunks or stages in one batch flow.

### Boundary

Use `pipeline-filter` when data or requests move through a sequence of independent transformation stages connected by well-defined outputs and inputs.

Do not use it for any multi-step function. The key signal is separable filter stages composed into a pipeline.
