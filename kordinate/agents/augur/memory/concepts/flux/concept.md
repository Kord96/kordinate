---
description: Flux/Redux (Unidirectional Data Flow) architectural pattern
type: pattern
testable: true
curated: true
scope: global
preloaded: none
graphable: true
abstraction: [architectural, frontend, data]
---
# Flux/Redux (Unidirectional Data Flow)

## Recognition

How to identify this pattern in code.

### Signatures

- Central store holding application state as a single source of truth with `dispatch(action)` API
- Reducers or mutations as pure functions transforming state: `(state, action) => newState`
- `actions/`, `reducers/`, `mutations/`, `slices/` directories containing state management code
- `useSelector()`, `useDispatch()`, `connect()`, `mapState()`, `mapGetters()` in UI code
- Libraries: Redux (`createStore`, `combineReducers`), Vuex (`createStore`, `mutations`), NgRx (`StoreModule`, `createReducer`), Redux Toolkit (`createSlice`, `configureStore`)

**Not this pattern:** A backend `store` variable (e.g., key-value store, session store) is not the flux pattern. Flux/Redux is specifically a frontend unidirectional data flow pattern with actions, reducers/mutations, and a centralized store that UI components subscribe to. The presence of the word "store", "dispatch", or "action" alone in backend code does not indicate flux.

### Confidence

- **high** -- Redux/Vuex/NgRx library imports with explicit `dispatch(action)`, reducer functions, and component bindings
- **medium** -- Custom centralized state management with defined mutations and unidirectional flow mimicking flux
- **low** -- State container with event-driven updates that loosely follows unidirectional flow

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
