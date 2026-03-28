---
description: Strategy architectural pattern
type: pattern
testable: true
curated: true
scope: global
preloaded: none
graphable: true
abstraction: [design]
---
# Strategy

## Recognition

How to identify this pattern in code.

### Signatures

- Interface/protocol with a single method implemented by multiple concrete classes
- Strategy selection via configuration, environment variable, or runtime parameter
- Classes ending in `Strategy`, `Policy`, `Algorithm`, `Handler`
- Python: protocol/ABC with multiple implementations, function passed as strategy (callable)
- Java/TS: interface with `execute()`/`apply()`/`process()` method and multiple implementations
- Go: function type or interface with multiple implementations assigned at init
- Go: interface type with 2+ concrete implementations in separate files, selected at construction time (e.g., `Pacer` interface with `LeakyBucketPacer`, `NoOpPacer` implementations; or `Storage` interface with `LocalStorage`, `RedisStorage`)

### Confidence

- **high** -- interface with one core method, multiple implementations, and runtime selection logic
- **medium** -- config-driven selection between interchangeable implementations of the same operation
- **low** -- if/else or switch choosing between inline algorithm variants

## Architecture

Look for clean separation between strategy selection and strategy execution.

### Review Checklist

- All strategies implement the same interface with identical input/output contracts
- Strategy selection is externalized (config, factory, or parameter), not hardcoded
- Context class delegates to the strategy without knowing which concrete strategy is active
- Adding a new strategy does not require modifying existing strategies or the context
- Strategies are stateless or their state is scoped to a single execution

### Anti-patterns

- Strategy interface with methods only some implementations use (interface segregation violation)
- Context class containing fallback logic that bypasses the strategy
- Strategies that depend on each other or share mutable state
- Using strategy pattern when a simple function parameter would suffice (over-engineering)
