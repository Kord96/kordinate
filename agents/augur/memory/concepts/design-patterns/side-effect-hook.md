---
kind: concept
name: side-effect-hook
signatures: {}
type: pattern
abstraction:
- frontend
- lifecycle
scope: frontend
status: primary
family: design-patterns
---

# Explanation

## Recognition

How to identify this pattern in code.

### Signatures

- `useEffect` and `useLayoutEffect` with dependency arrays and cleanup returns (React)
- `onMounted`, `onUnmounted`, `watch`, `watchEffect` lifecycle and reactive watchers (Vue)
- `ngOnInit`, `ngOnDestroy`, `ngOnChanges` lifecycle hooks (Angular)
- `onMount`, `onDestroy`, `afterUpdate` lifecycle functions (Svelte)
- Cleanup functions returned from effect callbacks (unsubscribe, clearInterval, abort controller)
- Dependency arrays controlling when effects re-run: `[dep1, dep2]`, empty `[]` for mount-only
- `useInsertionEffect` for CSS-in-JS library injection before DOM mutations (React)
- Subscription setup and teardown patterns: `subscribe()`/`unsubscribe()`, `addEventListener`/`removeEventListener`
- `AbortController` created in effect and aborted in cleanup for fetch cancellation

### Confidence

- **high** -- Framework effect hook or lifecycle method with explicit dependency tracking, cleanup function, and clear separation from render logic
- **medium** -- Lifecycle method that performs side effects (API calls, subscriptions) but lacks proper cleanup or dependency management
- **low** -- Imperative code inside render or template that triggers side effects without lifecycle awareness

## Architecture

Look for side effects that are bound to component lifecycle, execute at the right time relative to rendering, and clean up properly on unmount or dependency change.

### Review Checklist

- Every subscription, timer, or listener set up in an effect has a corresponding cleanup
- Dependency arrays are complete and accurate -- no missing dependencies causing stale closures
- Effects that should run once (on mount) use an empty dependency array, not missing dependencies
- Data fetching effects handle race conditions (stale closure, component unmounted before response)
- Heavy effects are debounced or throttled to avoid performance issues on rapid re-renders
- Effects are not used for state derivation that could be computed synchronously during render

### Anti-patterns

- Missing cleanup functions causing memory leaks (orphaned subscriptions, dangling timers)
- Incorrect or missing dependency arrays causing effects to run too often or with stale data
- Using effects for derived state that should be computed with useMemo, computed properties, or selectors
- Fetch-in-effect without cancellation, causing state updates on unmounted components
- Chained effects where one effect sets state that triggers another effect (effect cascade)

### Relationship To Other Concepts

- Related to [component](/concepts/component) because side-effect hooks are lifecycle tools attached to component composition boundaries.
- Related to [reactive-store](/concepts/reactive-store) when effects subscribe to or synchronize with client-side reactive state containers.
- Related to [hidden-side-effects](/concepts/hidden-side-effects) because poorly scoped hooks can make side effects feel implicit and hard to reason about.

### Boundary

Use `side-effect-hook` when lifecycle-bound hooks are the explicit mechanism for running and cleaning up side effects around component rendering.

Do not use it for any callback or imperative helper that is not tied to a component or reactive lifecycle.
