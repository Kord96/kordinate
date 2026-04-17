---
description: Component-oriented UI library for declarative rendering, client hydration, and async boundary composition
---
# React

React is a component-oriented UI library for declarative rendering, client hydration, and async boundary composition.

## Recognition
Common signals:
- `react` or `react-dom` dependency
- JSX or TSX component files
- imports from `react` or `react-dom/client`
- hooks such as `useState`, `useEffect`, or `useReducer`
- `createRoot()` or `hydrateRoot()` bootstrap code

## Architectural implications
- component trees are the dominant unit of UI composition
- server rendering and hydration may be present, but only when the surrounding stack enables it
- async loading and failure handling often appear through suspense and error boundary patterns

## Common failure modes
- prop drilling across deep trees
- state scattered across ad hoc hooks without clear ownership
- data fetching leaking into presentation components
