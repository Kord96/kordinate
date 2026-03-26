---
description: Suspense Boundary — declarative loading state management for async component trees
type: pattern
testable: true
curated: true
scope: global
preloaded: none
graphable: true
abstraction: [frontend, lifecycle]
---
# Suspense Boundary

## Recognition

How to identify this pattern in code.

### Signatures

- `<Suspense fallback={...}>` (React)
- `<Suspense>` with `#fallback` template slot (Vue 3)
- `@defer` blocks (Angular 17+)
- `{#await}` blocks (Svelte)
- Nested suspense boundaries for granular loading states
- `useTransition` / `startTransition` for non-blocking updates (React)
- Streaming SSR with progressive hydration

### Confidence

- **high** -- explicit `<Suspense>` with fallback UI, nested boundaries for different loading zones
- **medium** -- framework provides implicit suspense (Next.js `loading.tsx`, Nuxt `<NuxtLoadingIndicator>`)
- **low** -- manual loading state management (`isLoading` flags) without declarative boundaries

## Architecture

Look for declarative boundaries that manage the loading state of async subtrees, providing fallback UI while suspended children resolve their data or code.

### Review Checklist

- Each async data boundary has its own Suspense wrapper (not one giant boundary)
- Fallback UI matches the layout of the loaded content (skeleton, not spinner)
- Nested boundaries prevent cascade (one slow component doesn't block siblings)
- Error boundaries are paired with suspense boundaries for failed loads
- SSR streaming is enabled when using server-side suspense

### Anti-patterns

- Single top-level Suspense wrapping the entire app (all-or-nothing loading)
- Suspense without paired error boundary (unhandled async failures)
- Using Suspense for synchronous conditional rendering (misuse of the pattern)
- Waterfall loading -- nested suspense that serializes parallel fetches
