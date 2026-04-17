---
description: "Server Prefetch \u2014 fetching data on the server before client rendering"
type: pattern
graphable: true
abstraction:
- frontend
- data
status: primary
scope: frontend
relationships:
  related_to:
  - hydration
  - lazy-loading
  - suspense-boundary
aliases: []
disambiguates_from: []
preferred_over: []
implies: []
anti_signals: []
detector_coverage: partial
examples: []
---
# Server Prefetch

## Recognition

How to identify this pattern in code.

### Signatures

- `loader` functions with `queryClient.prefetchQuery` and `dehydrate` (React Router + TanStack Query)
- `getServerSideProps` returning `{ props }` for per-request server data (Next.js Pages Router)
- `getStaticProps` with optional `revalidate` for ISR (Next.js Pages Router)
- Server Components with direct `await` on data fetches, no client hooks (Next.js App Router)
- `useAsyncData` and `useFetch` composables executing on the server during SSR (Nuxt)
- `load` function in `+page.server.ts` or `+page.ts` (SvelteKit)
- `resolve` guards in route configuration fetching data before component activation (Angular)
- `prefetchQuery`, `ensureQueryData` called outside component lifecycle for cache priming
- `HydrationBoundary` or `DehydratedState` props passing serialized query cache to the client
- `__NEXT_DATA__` or inline `<script>` tags containing serialized server state in HTML

### Confidence

- **high** -- Framework-specific server data function (loader, getServerSideProps, load) with explicit cache dehydration and client hydration boundary
- **medium** -- Data fetched in a server context and passed to client components via props or serialized state, but without formal hydration utilities
- **low** -- API calls made in server middleware or route handlers where the result is injected into the page but without structured cache management

## Architecture

Look for data fetching that runs on the server during the request lifecycle, with results serialized into the response and rehydrated on the client to avoid redundant fetches.

### Review Checklist

- Server-fetched data is serialized in a format the client cache can consume (dehydrated state)
- Hydration boundary is placed so the client does not refetch data that was already loaded on the server
- Error handling covers server fetch failures with appropriate fallback or error page
- Cache keys are consistent between server prefetch and client-side queries
- Sensitive data (tokens, internal IDs) is not leaked through serialized state in the HTML
- Stale-while-revalidate or cache TTL is configured to balance freshness and performance

### Anti-patterns

- Prefetching on the server but also triggering the same fetch on client mount (double fetch)
- Serializing the entire server response into HTML instead of only the data the page needs
- No error boundary around hydration, causing full-page crashes on deserialization failure
- Using server prefetch for user-specific data on statically generated pages (cache poisoning)
- Mismatched cache keys between server and client causing hydration misses

### Relationship To Other Concepts

- Related to [hydration](/concepts/hydration) because server-prefetched data is often serialized into the response and resumed on the client.
- Related to [lazy-loading](/concepts/lazy-loading) because prefetching and deferred loading are complementary strategies for shaping perceived performance.
- Related to [suspense-boundary](/concepts/suspense-boundary) when loading boundaries coordinate server-fetched and client-resumed data dependencies.

### Boundary

Use `server-prefetch` when the server intentionally loads data ahead of client render and passes it forward to avoid an immediate duplicate client fetch.

Do not use it for generic SSR or any backend API call that is not specifically preparing client render state.
