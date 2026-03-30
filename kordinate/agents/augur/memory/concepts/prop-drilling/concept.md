---
description: Prop Drilling anti-pattern
type: anti-pattern
graphable: false
---
# Prop Drilling

## Recognition

How to identify this anti-pattern in code.

### Signatures

- Same prop passed through 5+ component layers unchanged
- Intermediate components accepting and forwarding props they do not use in their own render logic
- "Tunneling" data through the component tree to reach a deeply nested child
- Component signatures with many props that are just pass-through for children
- Adding a new prop to a leaf component requires modifying every ancestor in the chain
- Props named identically across a chain of parent-child components with no transformation

### Confidence

- **high** -- a prop is threaded through 5 or more component levels, with intermediate components only forwarding it to children and never reading it, confirmed by tracing the prop through the component tree
- **medium** -- intermediate components accept props they do not reference in their own JSX/template, only passing them down via spread or explicit forwarding
- **low** -- a component's prop list includes several items that seem unrelated to its own responsibility, suggesting it is acting as a pass-through

## Impact

Fragile component hierarchy where adding, removing, or renaming a prop requires changes across many files, making refactoring painful.

### Symptoms

- Adding a feature to a leaf component requires modifying 5+ intermediate component files
- Intermediate components have bloated prop interfaces full of pass-through data
- Renaming a prop cascades into changes across many unrelated components
- Component reuse is difficult because components carry implicit dependencies on their position in the tree
- TypeScript or PropTypes definitions grow large with props the component itself does not use

### Remediation

- Use React Context, Vue provide/inject, or Angular services to make shared state available to deeply nested components without threading through intermediaries
- Adopt a state management library (Redux, Zustand, Pinia) for cross-cutting data that many components need
- Apply the composition pattern: pass children as props or slots so intermediate components do not need to know about leaf component data
- Restructure the component tree to flatten unnecessary nesting and reduce the depth data must travel
- Use the render props or compound component pattern to co-locate data requirements with the components that use them
