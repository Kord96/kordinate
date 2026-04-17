---
description: Adapter architectural pattern
type: pattern
testable: true
graphable: true
abstraction:
- design
- integration
status: primary
scope: cross-cutting
relationships:
  related_to:
  - anti-corruption-layer
  - hexagonal
  - gateway-backends
aliases: []
disambiguates_from: []
preferred_over: []
implies: []
anti_signals: []
detector_coverage: rich
examples: []
---
# Adapter

## Recognition

How to identify this pattern in code.

### Signatures

- Classes named `*Adapter`, `*Gateway`, `*Wrapper`
- Translating one interface to match another expected by the caller
- Wrapper around third-party libraries isolating external API changes
- Anti-corruption layer between bounded contexts or legacy systems (see also: anti-corruption-layer)
- Import of external SDK with a thin local interface in front of it
- `adapt()`, `convert()`, `translate()` functions bridging two APIs

### Confidence

- **high** -- Class that implements a target interface by delegating to an adaptee with a different interface, with explicit mapping between the two
- **medium** -- Thin wrapper around a third-party library exposing a simplified or project-specific interface
- **low** -- Utility function that converts between two data formats without a formal adapter class

## Architecture

Adapter translates one interface to match another. Look for clean separation between the target interface and the adaptee, with mapping logic isolated in the adapter.

### Review Checklist

- Adapter maps cleanly between target and adaptee interfaces without leaking adaptee types to callers
- Third-party dependencies are wrapped so swapping the vendor only changes the adapter
- Error translation is handled -- adaptee exceptions are mapped to domain-appropriate errors
- Adapter is stateless where possible, holding no mutable state beyond the adaptee reference

### Anti-patterns

- Leaky adapter that exposes adaptee types or exceptions to callers (defeats the purpose)
- Adapter with business logic -- it should only translate, not make decisions
- No adapter at all -- third-party types used directly throughout the codebase making vendor migration painful

### Relationship To Other Concepts

- Related to [anti-corruption-layer](/concepts/anti-corruption-layer) because adapters are a common implementation mechanism for isolating external systems from internal models.
- Related to [hexagonal](/concepts/hexagonal) because adapters often implement ports on the outside of a hexagonal boundary.
- Related to [gateway-backends](/concepts/gateway-backends) when an adapter hides upstream protocol or schema details behind a cleaner service-facing interface.

### Boundary

Use `adapter` when the important observation is translation between one interface and another so the caller does not depend directly on the adaptee’s surface.

Do not use it for every wrapper class. A wrapper becomes an adapter when interface translation or compatibility is the main architectural purpose.
