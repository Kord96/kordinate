---
description: Entity-Component-System (ECS) architectural pattern
type: pattern
testable: true
graphable: true
abstraction:
- architectural
- realtime
status: primary
scope: cross-cutting
relationships:
  related_to:
  - component
  - game-loop
  - tick-simulation
aliases: []
disambiguates_from: []
preferred_over: []
implies: []
anti_signals: []
detector_coverage: partial
examples: []
---
# Entity-Component-System (ECS)

## Recognition

How to identify this pattern in code.

### Signatures

- Entities represented as plain integer IDs or opaque handles, not class hierarchies
- Components are pure data structs with no behavior (e.g., `Position`, `Velocity`, `Health`)
- Systems are functions that iterate over entities matching a component query
- Central `World` or `Registry` object that owns all entities and components
- Methods like `add_component()`, `remove_component()`, `query()`, `spawn()`
- Component storage organized by type (struct-of-arrays) rather than by entity
- Libraries: Bevy ECS (Rust), entt (C++), bitecs (JS), esper (Python), flecs (C/C++), legion (Rust)

### Confidence

- **high** — `World`/`Registry` class with `add_component()`/`query()` methods and entity IDs as integers
- **medium** — pure data structs paired with standalone processing functions, no inheritance hierarchy for game objects
- **low** — integer IDs used as keys into multiple parallel arrays or maps

## Architecture

Look for strict separation of identity (entities), data (components), and behavior (systems).

### Review Checklist

- Entities are plain IDs with no embedded data or methods
- Components contain only data, never logic or references to other components
- Systems declare their component dependencies explicitly via queries
- World/Registry is the single owner of all entity-component relationships
- Component queries use archetypes or bitmasks for efficient iteration
- Systems can run in parallel when their component access does not overlap

### Anti-patterns

- Components that hold methods or reference other components directly
- Systems that store state between ticks instead of reading from components
- Entity IDs used as indices into a single monolithic struct (god object)
- Inheritance hierarchies for entities instead of composition via components

### Relationship To Other Concepts

- Related to [component](/concepts/component) because ECS decomposes behavior around componentized data, though ECS components are data-only rather than UI or service modules.
- Related to [game-loop](/concepts/game-loop) because ECS systems are often executed as ordered stages inside a realtime loop.
- Related to [tick-simulation](/concepts/tick-simulation) because ECS frequently advances world state in discrete update ticks.

### Boundary

Use `entity-component-system` when entities, components, and systems are explicitly separated so behavior iterates over data-oriented component sets.

Do not use it for any composition-heavy object model or plugin system.
