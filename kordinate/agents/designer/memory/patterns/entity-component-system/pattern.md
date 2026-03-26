---
description: Entity-Component-System (ECS) architectural pattern
type: pattern
testable: true
curated: true
scope: global
preloaded: none
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
