---
description: Facade architectural pattern
type: pattern
testable: true
curated: true
scope: global
preloaded: none
graphable: true
abstraction: [design]
---
# Facade

## Recognition

How to identify this pattern in code.

### Signatures

- Classes explicitly named `*Facade` that wrap complex subsystems behind a simplified interface
- Python: `__init__.py` re-exporting a simplified public API from a complex package (5+ `from .X import Y` lines)
- Python: module-level convenience functions (`validate()`, `parse()`, `render()`) that hide complex internal machinery
- Java: classes named `*Facade` providing simplified access to a subsystem
- TypeScript: SDK client class wrapping multiple subsystems behind a simple API (`.send()`, `.message()`, `.action()`)
- Go: struct explicitly named `*Facade` coordinating multiple subsystem interfaces

### Negative signals (not sufficient for detection)

- Classes named `*Client`, `*Gateway`, `*Manager`, or `*Service` are NOT automatically facades -- these are common naming conventions for many patterns (adapter, gateway, service layer)
- `App`, `Bot`, `Engine`, or `Server` entry point classes are application bootstrapping, not the facade pattern
- A service class injecting multiple collaborators is normal service composition, not a facade unless it explicitly simplifies a complex subsystem API for external consumers
- The word `facade` in comments or package names without an actual simplifying wrapper class is not the pattern
- Spring `@Service` classes with multiple injected dependencies are standard service layer, not facade

### Confidence

- **high** -- Class explicitly named Facade wrapping multiple subsystem classes with simplified methods
- **medium** -- Wrapper module/class providing high-level operations that delegate to multiple internal components, or `*Client`/`*Manager` classes coordinating 3+ subsystems
- **low** -- `__init__.py` with selective re-exports or a convenience function wrapping library calls

## Architecture

Look for clean simplification of complex subsystems without adding logic.

### Review Checklist

- Facade delegates to subsystem classes, does not contain business logic itself
- Subsystem classes remain usable directly for advanced use cases
- Facade does not become a god object — one facade per cohesive subsystem
- Facade interface is stable even as subsystem internals change
- No circular dependency between facade and subsystem classes

### Anti-patterns

- Facade that adds business logic instead of just simplifying access
- Single facade wrapping the entire application (becomes god object)
- Facade that makes subsystem classes inaccessible (forced indirection)
- Nested facades (facade wrapping facade wrapping subsystem)
