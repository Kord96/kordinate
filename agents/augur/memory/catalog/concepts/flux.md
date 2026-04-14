---
description: Flux/Redux (Unidirectional Data Flow) architectural pattern
type: pattern
testable: true
graphable: true
abstraction: [architectural, frontend, data]
---
# Flux/Redux (Unidirectional Data Flow)

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
