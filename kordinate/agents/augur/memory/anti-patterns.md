---
description: Index of recognized anti-patterns by category
---
# Anti-Patterns Index

22 anti-patterns across 6 categories. Each has recognition signatures and remediation steps.

## Categories

| Category | Key Question |
|----------|-------------|
| code-structure | Is the codebase organized and maintainable? |
| dependencies | Are dependencies clean and acyclic? |
| data | Is data accessed and modeled correctly? |
| concurrency | Is concurrent code safe and readable? |
| api | Are interfaces well-designed and efficient? |
| operations | Are errors handled and config managed cleanly? |

## Anti-Patterns

### Code Structure

| Anti-pattern | What to look for | Reference |
|-------------|-----------------|-----------|
| God object | Classes with 1000+ lines touching many unrelated concerns | [view](concepts/god-object/pattern.md) |
| Spaghetti code | Deeply nested conditionals, 500+ line functions, untraceable flow | [view](concepts/spaghetti-code/pattern.md) |
| Lava flow | Dead code, commented-out blocks, unreachable branches | [view](concepts/lava-flow/pattern.md) |
| Golden hammer | One tool/framework forced onto every problem | [view](concepts/golden-hammer/pattern.md) |
| Cargo cult | Patterns applied without understanding (factory for one type, etc.) | [view](concepts/cargo-cult/pattern.md) |
| Big ball of mud | No directory structure, any file imports any other | [view](concepts/big-ball-of-mud/pattern.md) |

### Dependencies

| Anti-pattern | What to look for | Reference |
|-------------|-----------------|-----------|
| Circular dependency | A imports B imports A (direct or transitive) | [view](concepts/circular-dependency/pattern.md) |
| Tight coupling | Concrete class references everywhere, no interfaces | [view](concepts/tight-coupling/pattern.md) |
| Leaky abstraction | Implementation details in interface signatures | [view](concepts/leaky-abstraction/pattern.md) |

### Data

| Anti-pattern | What to look for | Reference |
|-------------|-----------------|-----------|
| N+1 queries | Database query inside a loop, ORM lazy loading in iteration | [view](concepts/n-plus-one/pattern.md) |
| Premature optimization | Caching/denormalizing before measuring, complex structures for small data | [view](concepts/premature-optimization/pattern.md) |
| Stringly typed | Strings where enums/types should be, string comparison for branching | [view](concepts/stringly-typed/pattern.md) |
| Magic numbers | Hardcoded values with no explanation | [view](concepts/magic-numbers/pattern.md) |

### Concurrency

| Anti-pattern | What to look for | Reference |
|-------------|-----------------|-----------|
| Race condition | Unsynchronized read-modify-write on shared state | [view](concepts/race-condition/pattern.md) |
| Deadlock | Multiple locks acquired in inconsistent order | [view](concepts/deadlock/pattern.md) |
| Callback hell | Deeply nested callbacks, pyramid-shaped code | [view](concepts/callback-hell/pattern.md) |

### API / Interface

| Anti-pattern | What to look for | Reference |
|-------------|-----------------|-----------|
| Chatty API | 10+ sequential calls to assemble one view, no batch endpoints | [view](concepts/chatty-api/pattern.md) |
| Anemic domain model | Model classes with only getters/setters, all logic in services | [view](concepts/anemic-domain-model/pattern.md) |
| God endpoint | Single route handling multiple operations via action parameter | [view](concepts/god-endpoint/pattern.md) |

### Operations

| Anti-pattern | What to look for | Reference |
|-------------|-----------------|-----------|
| Log and throw | Same exception logged at multiple layers | [view](concepts/log-and-throw/pattern.md) |
| Swallowed exception | Empty catch/except blocks, errors silently ignored | [view](concepts/swallowed-exception/pattern.md) |
| Config sprawl | Config in env vars AND yaml AND code AND database, no single source of truth | [view](concepts/config-sprawl/pattern.md) |
