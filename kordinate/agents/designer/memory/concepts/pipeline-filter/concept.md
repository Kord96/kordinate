---
description: Pipeline/Filter architectural pattern
type: pattern
testable: true
curated: true
scope: global
preloaded: none
graphable: true
abstraction: [design, data]
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
- Java: Netty `ChannelPipeline` with `addLast()`/`addFirst()` ordered handler chain
- Java: Spring `GatewayFilterChain`, Servlet `FilterChain`, Spring Security `SecurityFilterChain` with ordered filter execution
- Java: Composite recipe/rule patterns where transforms are chained: `CompositeRecipe`, `RecipeList`, `addRecipe()`
- Go: sequential interface wrapping chains where each stage takes an input interface and returns the same type with added processing (e.g., interceptor chains, `io.Reader`/`io.Writer` wrapping, gRPC interceptors)
- Go: `for _, handler := range handlers { reader = handler.Process(reader) }` -- iterating a slice of handlers, each wrapping the previous result

**Not this pattern (Python):** A class named `*Pipeline` in a project that is not about data processing (e.g., CI/CD pipeline configuration, ML pipeline metadata, request pipeline in a web framework) may use the word "pipeline" without implementing the pipeline-filter pattern. The pattern requires sequential transform functions with a uniform interface. `pipe()` in RxPY or functional composition is pipeline-filter; `Pipeline` as a container for steps in a web framework's middleware chain is middleware, not pipeline-filter.

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
