---
description: Hydration — transferring server-rendered state to the client for interactive rendering
type: pattern
curated: true
scope: global
preloaded: none
graphable: true
abstraction: [frontend, data]
---
# Hydration

## Recognition

How to identify this pattern in code.

### Signatures

- `dehydrate(queryClient)` and `HydrationBoundary` or `Hydrate` component (TanStack Query)
- `hydrateRoot` replacing `createRoot` for server-rendered HTML (React 18+)
- `ReactDOM.hydrate` for attaching to server-rendered markup (React pre-18)
- `createSSRApp` instead of `createApp` for server-side rendered Vue applications (Vue)
- `TransferState` and `makeStateKey` for transferring state from server to client (Angular)
- `useId()` for generating stable IDs that match between server and client renders
- `__NEXT_DATA__` script tag containing serialized page props (Next.js)
- `window.__NUXT__` payload containing server-fetched state (Nuxt)
- `<script>` tags with `type="application/json"` or data attributes containing serialized state in SSR output
- Hydration mismatch warnings in console: "Text content did not match", "Hydration failed"
- `suppressHydrationWarning` prop on elements with expected mismatches (React)

### Confidence

- **high** -- Framework SSR hydration API (hydrateRoot, createSSRApp, TransferState) with serialized state embedded in HTML and client-side rehydration consuming it
- **medium** -- Server-rendered HTML with inline JSON state that client JavaScript reads on load to initialize components, but without formal hydration API
- **low** -- Any server-rendered page where client JavaScript reads embedded data attributes or hidden fields to bootstrap state

## Architecture

Look for a two-phase rendering process: server generates HTML with embedded state, client attaches event handlers and restores state without re-fetching or re-rendering from scratch.

### Review Checklist

- Server and client render the same component tree with the same data to avoid hydration mismatches
- Serialized state does not include sensitive data (auth tokens, internal IDs, PII) that should not be in HTML source
- Hydration errors are treated as bugs and fixed, not suppressed globally
- State serialization handles edge cases: undefined, Date objects, BigInt, circular references
- Hydration boundary is placed at the correct level so client-only components are excluded from server render
- Performance: serialized state payload size is monitored and kept reasonable

### Anti-patterns

- Suppressing all hydration warnings instead of fixing the root cause of server/client mismatches
- Serializing enormous data payloads into HTML, bloating document size and time-to-interactive
- Client components that immediately refetch data already available in hydrated state
- Server render depending on browser-only APIs (window, document) causing mismatch or crash
- No hydration boundary around client-only components, causing server render to fail or diverge
