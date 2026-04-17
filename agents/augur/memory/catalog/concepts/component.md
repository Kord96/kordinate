---
description: Component Architecture architectural pattern
type: pattern
testable: true
graphable: true
abstraction:
- design
- frontend
status: primary
scope: frontend
relationships:
  related_to:
  - mvc
  - mvvm
  preferred_over:
  - component-slot
aliases: []
disambiguates_from: []
preferred_over:
- component-slot
implies: []
anti_signals: []
detector_coverage: partial
examples: []
---
# Component Architecture

## Recognition

How to identify this pattern in code.

### Signatures

- Self-contained UI components with props/state, composed into a tree
- `render()`, `template`, or JSX/TSX returning UI markup from component logic
- Component files: `.jsx`, `.tsx`, `.vue`, `.svelte`, or `@Component` decorators
- Props passed down, events emitted up (unidirectional data flow within the tree)
- Libraries: React, Vue, Svelte, Angular components, Web Components (`customElements.define`)

### Confidence

- **high** -- Framework component files with explicit props interface, local state, and render function
- **medium** -- Reusable UI modules with encapsulated markup and behavior, but no formal component framework
- **low** -- Any UI code organized into isolated, composable pieces with some form of data passing

## Architecture

Look for a tree of self-contained, composable UI components with clear data flow through props and events.

### Relationship To Other Concepts

- `component` is the primary UI composition concept.
- `component-slot` is a specialized content-projection technique within a component system, not a separate primary architecture family.
- `mvvm` and `mvc` can coexist with components; they describe state/presentation coordination, not the rendering tree itself.
- Prefer `component` when the main structure is a tree of reusable UI units, even if some components expose slots, render props, or compound APIs.

### Review Checklist

- Components have a single responsibility -- not doing data fetching, rendering, and business logic in one component
- Props interface is explicit and typed (PropTypes, TypeScript interfaces, or equivalent)
- State is owned by the appropriate component -- lifted only when necessary for sibling communication
- Side effects (API calls, subscriptions) are isolated in lifecycle hooks or dedicated hooks/composables
- Components are reusable -- no hardcoded parent-specific assumptions

### Anti-patterns

- God components with hundreds of lines mixing data fetching, state management, and rendering
- Prop drilling through many levels instead of using context/provide-inject or state management
- Direct DOM manipulation bypassing the component framework's rendering cycle
- Tightly coupled components that import and reference each other's internal state

### Boundary

Use `component` when the important observation is this specific architectural concern within a frontend, UI, or client-side architectural concern.

Do not use a nearby alternative label when this concept more precisely matches the code and intent.
