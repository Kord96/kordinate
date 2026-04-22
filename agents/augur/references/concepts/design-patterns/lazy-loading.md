---
kind: concept
name: lazy-loading
signatures: {}
source:
  memory_concept: memory/catalog/concepts/lazy-loading.md
type: pattern
abstraction:
- frontend
- deployment
scope: frontend
status: primary
---

# Explanation

## Recognition

How to identify this pattern in code.

### Signatures

- `React.lazy(() => import(...))` and `<Suspense>` wrapper (React)
- `defineAsyncComponent(() => import(...))` (Vue)
- `loadChildren: () => import(...)` in route config (Angular)
- Dynamic `import()` expressions in route definitions
- Webpack magic comments (`/* webpackChunkName */`)
- Vite's automatic code splitting on dynamic imports
- `next/dynamic` (Next.js)
- Route-based splitting: each route in its own chunk

### Confidence

- **high** -- `React.lazy` or `defineAsyncComponent` with `Suspense`/loading boundary, visible chunk splitting in build output
- **medium** -- dynamic `import()` in route config but no explicit loading states
- **low** -- framework handles splitting automatically (e.g., Next.js pages) with no explicit lazy boundaries

## Architecture

Look for deferred loading of components or modules via dynamic imports, with loading state management and chunk optimization for the critical rendering path.

### Review Checklist

- Loading boundaries wrap lazy components with meaningful fallback UI (skeleton, spinner)
- Error boundaries catch failed chunk loads (network errors)
- Critical above-the-fold content is NOT lazy loaded
- Route-level splitting at minimum; component-level splitting for heavy widgets
- Preload hints for likely-needed chunks (`<link rel="prefetch">`)

### Anti-patterns

- Lazy loading everything including tiny components (overhead exceeds savings)
- No fallback UI -- user sees blank space during load
- No error handling for failed chunk loads (stale deployment, network failure)
- Splitting too granularly -- hundreds of tiny chunks increase HTTP request overhead

### Relationship To Other Concepts

- Related to [suspense-boundary](/concepts/suspense-boundary) because many modern frontend stacks use suspense-like boundaries to manage deferred loading states.
- Related to [server-prefetch](/concepts/server-prefetch) because prefetching and lazy loading are complementary strategies for controlling when data and code arrive.
- Related to [micro-frontend](/concepts/micro-frontend) because independently loaded frontend slices often rely heavily on lazy chunk loading.

### Boundary

Use `lazy-loading` when code or components are intentionally deferred until actually needed to reduce initial load cost.

Do not use it for ordinary pagination, backend demand loading, or any delayed operation that is not about deferred code or component loading.
