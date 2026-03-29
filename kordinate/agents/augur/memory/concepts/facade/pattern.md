---
description: Facade architectural pattern
type: pattern
testable: true
graphable: true
abstraction: [design]
---
# Facade

## Recognition

How to identify this pattern in code.

### Signatures

- Classes named `*Facade` or `*Gateway` or `*Client` that wrap complex subsystems
- Single entry point class providing simplified interface to a library or subsystem
- Methods that orchestrate multiple internal calls into one high-level operation
- Wrapper modules around third-party libraries (e.g., `email_service.py` wrapping SMTP + templates + attachments)
- `__init__.py` re-exporting a simplified public API from a complex package
- SDK client classes that hide REST/gRPC details behind method calls

### Confidence

- **high** — Class explicitly named Facade wrapping multiple subsystem classes with simplified methods
- **medium** — Wrapper module/class providing high-level operations that delegate to multiple internal components
- **low** — `__init__.py` with selective re-exports or a convenience function wrapping library calls

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
