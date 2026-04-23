---
kind: concept
name: reactive-store
signatures: {}
type: pattern
abstraction:
- frontend
- data
scope: frontend
status: primary
family: design-patterns
---

# Explanation

## Recognition

How to identify this pattern in code.

### Signatures

- `zustand` with `create()`, selector hooks, `set`/`get` state functions (React)
- `@reduxjs/toolkit` with `createSlice`, `configureStore`, `useSelector`, `useDispatch` (React)
- `redux` with `createStore`, `combineReducers`, `connect`, action creators (React)
- `pinia` with `defineStore`, `storeToRefs`, option or setup store syntax (Vue)
- `vuex` with `createStore`, `mapState`, `mapGetters`, `mutations`, `actions` (Vue)
- `@ngrx/store` with `StoreModule`, `createReducer`, `createSelector`, `select` (Angular)
- `svelte/store` with `writable`, `readable`, `derived`, `$store` auto-subscription syntax (Svelte)
- `jotai` with `atom`, `useAtom`, `useAtomValue`, `useSetAtom` (React)
- `recoil` with `atom`, `selector`, `useRecoilState`, `useRecoilValue` (React)
- `mobx` with `makeAutoObservable`, `observer`, `action`, `computed` (React)
- Store persistence middleware: `persist`, `createJSONStorage`, localStorage/sessionStorage integration
- Devtools integration: `redux-devtools`, `__REDUX_DEVTOOLS_EXTENSION__`

### Confidence

- **high** -- Dedicated state management library with store creation, typed selectors, and reactive subscriptions driving UI updates
- **medium** -- Centralized state object with manual subscription or context-based reactivity, but no formal store library
- **low** -- Module-level variables or singletons shared across components with ad-hoc change notification

## Architecture

Look for a centralized state container that components subscribe to reactively, with well-defined mutation paths and selector-based reads.

### Review Checklist

- Store is segmented by domain (slices, modules, or atoms) rather than a single monolithic object
- State mutations go through defined actions or setters, never direct object mutation
- Selectors derive computed values instead of duplicating state
- Subscriptions are scoped so components only re-render when their selected slice changes
- Async operations (API calls) are separated from synchronous state updates
- Persistence and hydration are handled by middleware, not ad-hoc serialization in components

### Anti-patterns

- Storing server-fetched data in a client store instead of using a server-state library (TanStack Query, SWR)
- Every component subscribing to the entire store instead of selecting specific slices
- Duplicating derived data in the store instead of computing it with selectors
- Mixing UI state (modal open, tab index) and domain state (user, cart) in the same store slice
- No devtools integration, making state changes opaque during development

### Relationship To Other Concepts

- Related to [flux](/concepts/flux) because many reactive stores implement unidirectional update flow and centralized state ideas.
- Related to [component](/concepts/component) because reactive stores usually feed UI trees and trigger component re-rendering or subscription updates.
- Related to [suspense-boundary](/concepts/suspense-boundary) when reactive state coordinates async readiness or data availability in the UI.

### Boundary

Use `reactive-store` when client-side state is held in a store that notifies subscribers reactively as state changes.

Do not use it for any state variable or context provider. The key signal is a dedicated reactive state container abstraction.
