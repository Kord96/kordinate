---
description: Adapter/Facade architectural pattern
curated: true
scope: global
preloaded: none
---
# Adapter/Facade

## Recognition

How to identify this pattern in code.

### Signatures

- Classes named `*Adapter`, `*Facade`, `*Gateway`, `*Wrapper`
- Translating one interface to another to make incompatible systems work together
- Facade simplifying a complex subsystem behind a single unified interface
- Wrapper around third-party libraries isolating external API changes
- Anti-corruption layer between bounded contexts or legacy systems
- Import of external SDK with a thin local interface in front of it
- `adapt()`, `convert()`, `translate()` functions bridging two APIs

### Confidence

- **high** -- Class that implements a target interface by delegating to an adaptee with a different interface, with explicit mapping between the two
- **medium** -- Thin wrapper around a third-party library exposing a simplified or project-specific interface
- **low** -- Utility function that converts between two data formats without a formal adapter class

## Architecture

Look for clean separation between the target interface and the adaptee, with mapping logic isolated in the adapter.

### Review Checklist

- Adapter maps cleanly between target and adaptee interfaces without leaking adaptee types to callers
- Facade provides a simplified interface without exposing subsystem internals
- Third-party dependencies are wrapped so swapping the vendor only changes the adapter
- Anti-corruption layer prevents external domain concepts from contaminating internal models
- Error translation is handled -- adaptee exceptions are mapped to domain-appropriate errors
- Adapter is stateless where possible, holding no mutable state beyond the adaptee reference

### Anti-patterns

- Leaky adapter that exposes adaptee types or exceptions to callers (defeats the purpose)
- God facade that wraps the entire subsystem surface area instead of exposing only needed operations
- Adapter with business logic -- it should only translate, not make decisions
- No adapter at all -- third-party types used directly throughout the codebase making vendor migration painful
