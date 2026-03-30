---
description: Side Effect Hook — lifecycle-bound execution of effects in component frameworks
type: pattern
graphable: false
abstraction: [frontend, lifecycle]
---
# Side Effect Hook

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
