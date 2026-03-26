---
description: Template Method architectural pattern
type: pattern
curated: true
scope: global
preloaded: none
---
# Template Method

## Recognition

How to identify this pattern in code.

### Signatures

- Abstract base class with a concrete method calling abstract/hook methods in sequence
- Hook methods: `_do_step()`, `_on_before()`, `_on_after()`, `_process()`, `_validate()`
- Subclasses override specific steps without changing the overall algorithm structure
- Python: `ABC` with mix of concrete and `@abstractmethod` methods, `_hook()` naming convention
- Java: abstract class with `final` template method calling abstract `doStep()` methods
- Go: embedded struct with interface for overridable steps
- Rust: trait with default method implementations calling required methods

### Confidence

- **high** -- abstract base class with a final/concrete orchestrating method calling abstract step methods, plus subclasses
- **medium** -- base class with overridable hook methods called in a fixed sequence
- **low** -- inheritance hierarchy where subclasses override some methods of a base class

## Architecture

Look for invariant algorithm structure in the base class with variation points in subclasses.

### Review Checklist

- Template method defines the algorithm skeleton and is not overridable (final/non-virtual)
- Hook methods have sensible defaults (not all abstract -- allow partial override)
- Subclasses override only the intended extension points, not the template method itself
- Base class documents which hooks are required vs optional
- Number of hooks is small (3-5); too many indicates the algorithm should be decomposed

### Anti-patterns

- Subclass overriding the template method itself, breaking the invariant structure
- Too many abstract methods forcing subclasses to implement everything (defeats the template)
- Hook methods with hidden ordering dependencies not documented in the base class
- Using inheritance for code reuse when composition (strategy) would be cleaner
