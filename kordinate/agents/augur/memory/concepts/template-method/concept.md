---
description: Template Method architectural pattern
type: pattern
testable: true
curated: true
scope: global
preloaded: none
graphable: true
abstraction: [design]
---
# Template Method

## Recognition

How to identify this pattern in code.

### Signatures

- Abstract base class with a concrete method calling abstract/hook methods in sequence
- Hook methods: `_do_step()`, `_on_before()`, `_on_after()`, `_process()`, `_validate()`
- Subclasses override specific steps without changing the overall algorithm structure
- Python: `ABC` with mix of concrete and `@abstractmethod` methods, `_hook()` naming convention
- Python: Mixin classes with a `run()` loop calling overridable hooks like `on_consume_ready()`, `on_iteration()`, `on_consume_end()` (e.g., Kombu `ConsumerMixin`)
- Python: Controller or base handler class defining `on_request()` / `on_response()` hooks that subclasses override to customize the request handling algorithm
- TypeScript/JavaScript: Abstract class with concrete orchestrating method calling abstract methods (e.g., `OCPPRequestService` defining `internalSendMessage` calling abstract `requestHandler`)
- TypeScript: Base middleware class defining lifecycle hooks (`onRunStart`, `onStepStart`, `transformInput`) that subclasses override selectively
- Java: abstract class with `final` template method calling abstract `doStep()` methods
- Go: embedded struct with interface for overridable steps -- look for a struct that embeds an interface and has a concrete method calling the interface methods in sequence

### Negative signals (not sufficient for detection)

- Go: a simple interface definition is not template method -- look for a concrete orchestrating function/method that calls interface methods in a fixed sequence
- Abstract base class that only defines abstract methods without any concrete orchestrating method is an interface, not template method
- A class with hooks but no fixed algorithm sequence (hooks called independently) is observer/plugin, not template method
- Rust: trait with default method implementations calling required methods
- Framework processing pipelines: abstract service classes where a concrete `process`/`handle` method calls overridable `preProcess`, `doProcess`, `postProcess` hooks in sequence
- Python: `@abstractmethod` alone is not template method. Many Python classes use `@abstractmethod` to define interfaces (strategy, adapter, plugin). Template method requires a *concrete* orchestrating method in the base class that calls the abstract methods in a fixed sequence. If there is no concrete orchestrating method, it is just an abstract base class or interface.
- Python: `raise NotImplementedError` in a method is a common Python idiom for "subclass must override this" -- equivalent to an interface, not template method, unless the caller is a concrete method in the same class
- TypeScript: `abstract` methods on a class are just interface definitions unless there is a concrete method in the same class that calls them in sequence. If all methods are abstract, it is an interface/strategy, not template method
- A base class with 3+ subclasses alone is not template method -- it could be strategy, adapter, or simple inheritance. Template method specifically requires a concrete orchestrating method in the base class that defines the algorithm skeleton

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
