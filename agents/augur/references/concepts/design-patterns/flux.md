---
kind: concept
name: flux
signatures: {}
source:
  memory_concept: memory/catalog/concepts/flux.md
type: pattern
abstraction:
- architectural
- frontend
- data
scope: frontend
status: primary
---

# Explanation

## Recognition

How to identify this pattern in code.

### Signatures

- Central store holding application state as a single source of truth
- Actions dispatched to describe state changes (`dispatch()`, action creators)
- Reducers or mutations as pure functions transforming state in response to actions
- `store`, `actions/`, `reducers/`, `mutations/`, `slices/` directories or files
- Libraries: Redux, Vuex/Pinia, MobX (with actions), NgRx, Zustand, Recoil

### Confidence

- **high** -- Explicit store with `dispatch(action)`, reducer functions, and `connect()`/`useSelector()` bindings
- **medium** -- Centralized state management with defined mutations and unidirectional flow, but non-standard naming
- **low** -- Any pattern where UI state flows in one direction through a central container

## Architecture

Look for a unidirectional cycle: view dispatches actions, reducers update the store, store notifies the view.

### Review Checklist

- Reducers are pure functions with no side effects (no API calls, no mutations of arguments)
- Actions are serializable plain objects -- no functions or class instances as payloads
- Side effects are handled in middleware, thunks, or sagas, not in reducers or components
- Store shape is normalized -- no deeply nested duplicate data
- Selectors derive computed state rather than storing redundant copies

### Anti-patterns

- Mutating store state directly instead of dispatching actions
- Putting API calls or async logic inside reducers
- Single monolithic reducer instead of composing smaller reducers per domain
- Every component connected to the global store instead of passing props from connected parents

### Relationship To Other Concepts

- Related to [reactive-store](/concepts/reactive-store) because many Flux-style systems implement central reactive stores.
- Related to [component](/concepts/component) because Flux shapes how state and actions flow through UI components.
- Related to [prop-drilling](/concepts/prop-drilling) because centralized unidirectional state flow is often introduced to reduce long prop chains.

### Boundary

Use `flux` when frontend state changes follow an explicit unidirectional flow through actions, stores, and view updates.

Do not use it for any global state library. The key signal is action-driven unidirectional data flow.
