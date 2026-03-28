---
description: Component Architecture architectural pattern
type: pattern
testable: true
curated: true
scope: global
preloaded: none
graphable: true
abstraction: [design, frontend]
---
# Component Architecture

## Recognition

How to identify this pattern in code.

### Signatures

- Self-contained UI components with props/state, composed into a tree
- `render()`, `template`, or JSX/TSX returning UI markup from component logic
- Component files: `.jsx`, `.tsx`, `.vue`, `.svelte`, or Angular `@Component` decorators
- Props passed down, events emitted up (unidirectional data flow within the tree)
- Libraries: React (`useState`, `useEffect`, functional components), Vue (`defineComponent`, `setup()`), Svelte, Angular, Web Components (`customElements.define`)

**Not this pattern:** Backend classes or modules named "component" are not the component architecture pattern. This pattern is specifically about UI component trees with props/state/render lifecycle. A service class named `AuthComponent` or a data structure named `ComponentConfig` is not evidence of this pattern.

### Confidence

- **high** -- Framework component files (`.jsx`/`.tsx`/`.vue`/`.svelte`) with explicit props interface, local state, and render function
- **medium** -- Reusable UI modules with encapsulated markup and behavior, but no formal component framework
- **low** -- Web Components (`customElements.define`) with shadow DOM and observed attributes

## Architecture

Look for a tree of self-contained, composable UI components with clear data flow through props and events.

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
