---
kind: concept
name: mediator
signatures: {}
source:
  memory_concept: memory/catalog/concepts/mediator.md
type: pattern
abstraction:
- design
- integration
scope: cross-cutting
status: primary
---

# Explanation

## Recognition

How to identify this pattern in code.

### Signatures

- Central coordinator class: `Mediator`, `EventBus`, `Dispatcher`, `Hub`, `Broker`
- Components communicate through the mediator, never directly referencing each other
- Methods: `send()`, `publish()`, `dispatch()`, `notify()` on a central object
- Request/response mediation: `mediatr` (C#), `mediator-py`, command/query dispatching
- Python: `mediator` pattern with `handle()` registry, event bus with typed handlers
- JS/TS: centralized event bus, message broker classes, Angular services mediating components
- Go: hub struct that routes messages between registered participants

### Confidence

- **high** -- central mediator object with registered components that communicate exclusively through it
- **medium** -- event bus with publish/subscribe where the bus is the only coupling between components
- **low** -- shared service that multiple components depend on for coordination

## Architecture

Look for reduced coupling: components know the mediator, not each other.

### Review Checklist

- Components have no direct references to other components (only to the mediator)
- Mediator logic is coordination only, not business logic (thin mediator)
- Communication contracts (message types) are well-defined
- Mediator does not become a god object accumulating all coordination logic
- Error in one component's handler does not break mediation for others

### Anti-patterns

- God mediator that contains business logic instead of just routing messages
- Components bypassing the mediator for "convenience" (breaking the pattern)
- Mediator with implicit ordering dependencies between handlers
- Untyped message passing where handler registration is stringly typed

### Relationship To Other Concepts

- Related to [observer](/concepts/observer) because both decouple participants, though a mediator centralizes collaboration rules instead of broadcasting events.
- Related to [command](/concepts/command) when commands are routed through one coordinator that chooses the appropriate handler.
- Related to [workflow-engine](/concepts/workflow-engine) when a central component coordinates step interactions without every participant knowing each other directly.

### Boundary

Use `mediator` when interaction between many components is centralized through one coordinator rather than encoded directly between peers.

Do not use it for any controller or service hub. The key signal is explicit decoupling of many participants through a mediator.
