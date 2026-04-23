---
kind: concept
name: component-slot
signatures: {}
type: pattern
abstraction:
- frontend
- design
scope: frontend
status: specialized
family: design-patterns
---

# Explanation

Treat this as a specialized technique under [component](/concepts/component), not as a separate primary UI architecture family.

## Recognition

How to identify this pattern in code.

### Signatures

- `children` prop for content projection and `Slot` component from Radix/headless libraries (React)
- `v-slot`, `<template #name>`, named and scoped slots with slot props (Vue)
- `<ng-content>`, `ContentChild`, `ContentChildren`, `select` attribute for named projection (Angular)
- `<slot>` element with `name` attribute and `let:` directive for passing data back (Svelte)
- Render props pattern: `render` or `children` as a function receiving data from the child (React)
- Compound components: `Select.Root`, `Select.Trigger`, `Select.Content` (Radix, Headless UI)
- `React.cloneElement` or `React.Children.map` for augmenting projected children
- Default slot content with fallback: `<slot>fallback</slot>`, `{children ?? <Default />}`
- `as` or `asChild` prop for polymorphic rendering (Radix, styled-components)

### Confidence

- **high** -- Framework slot API (v-slot, ng-content, Svelte slot) or explicit children/render prop pattern with named slots and scoped data passing
- **medium** -- Component accepts a `children` prop or render function and places it in its output, but without named slots or scoped data
- **low** -- Component renders arbitrary content via props (like a `label` string prop) but without true content projection

## Architecture

Look for a component that defines insertion points where parent-provided content is rendered, enabling flexible composition without the child dictating the content.

### Relationship To Other Concepts

- Prefer `component` as the primary UI architecture concept.
- Use `component-slot` only when content projection or slot contracts are the architectural point, not when the code merely contains reusable components.

### Review Checklist

- Slots have meaningful names when a component has multiple insertion points
- Scoped slots or render props provide only the data the parent needs, not the entire internal state
- Default slot content is provided for optional slots so the component works standalone
- TypeScript types or PropTypes define the expected shape of render props and scoped slot data
- Compound component context is properly scoped so nested sub-components do not leak state
- Slot content is not deeply coupled to the child's internal DOM structure

### Anti-patterns

- Passing complex JSX through regular props (like `header={<div>...</div>}`) instead of using slots or children for content projection
- Scoped slots that expose too much internal state, creating tight coupling between parent and child
- Using `React.cloneElement` to inject props into arbitrary children without type safety
- Compound components without context, requiring specific DOM nesting order that breaks when rearranged
- Overusing render props when simple children composition would suffice

### Boundary

Use `component-slot` when the important observation is this specific architectural concern within a frontend, UI, or client-side architectural concern.

Do not promote it above a broader parent concept unless the specialization itself is what materially explains the design.
