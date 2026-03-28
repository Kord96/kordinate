# Narrative Style Guide

Level 3 reference for illustrate-architecture. Read this before writing any narrative content.

## Structure

All narratives (`overview`, `structure_narrative`, flow/state/failure narratives) are chapters of one coherent story, not independent texts. Each assumes the reader has read the previous ones.

**Order**: overview (what is this system?) → structure (how is it organized?) → flows (what happens when users interact?) → state (where does truth live?) → failures (what happens when things break?)

**Zoom levels** (C4 model): Start at the highest abstraction, drill down. The reader should be able to stop at any depth and have a coherent understanding.

## Voice

**Scenario-driven**: Trace real user journeys. Name concrete actors and actions.

Good: "When Sarah opens the home page, **root-loader** fires a prefetch to **api-client**."
Bad: "The root loader component is responsible for prefetching data via the API client."

**Lead with action**: Start paragraphs with what happens, not setup.

Good: "**root-loader** fires a prefetch, creating a fresh QueryClient per request."
Bad: "When the request first arrives at the server, the system initializes and then the root-loader fires a prefetch."

**Decision anchors**: When mentioning a pattern or choice, briefly explain *why*.

Good: "The team uses **circuit-breaker** on the DummyJSON client — the API has long failure windows where retrying would just queue up timeouts."
Bad: "The system uses a circuit breaker pattern."

## Formatting

Narratives render in a bottom drawer panel — narrow, scrollable. Format accordingly.

**Paragraphs**: 2-3 sentences max. Separate with `\n\n` in the JSON string. Never write a single-paragraph wall of text.

**Headings**: Use `##` and `###` within longer narratives (structure_narrative, detailed flows) to create scannable sections. Headings become visual breaks in the drawer.

**Length targets**:
- `overview`: 2-3 sentences (~50 words)
- `structure_narrative`: 3-5 paragraphs with headings (~200 words)
- Flow narrative: 3-5 short paragraphs (~100-150 words)
- State narrative: 2-3 paragraphs (~80-120 words)
- Failure narrative: 3-4 paragraphs (~100-150 words)

**Punctuation**: Use em dashes (—) not double hyphens (--). Use periods, not semicolons, to end sentences.

## Cross-references

Narratives reference each other to create a connected story:

- Flow narratives mention failure modes: "this call is protected by a **circuit breaker** — see the DummyJSON Down failure scenario"
- Failure narratives reference flows: "when the SSR Prefetch flow hits this failure..."
- State narratives reference flows that read/write them: "the **Cart Flow** persists here after each add-to-cart action"

## Component references

Every `**bold component name**` in a narrative must match a `nodes[].id` or `nodes[].name`. The component renders these as clickable links that highlight the graph node. Don't bold text that isn't a component name.

## Examples

### Good flow narrative

```
**root-loader** fires a prefetch, creating a fresh QueryClient per request. It calls **categories-query** to fetch the full category list from **dummyjson**.

**home-loader** runs next, calling prefetchInfiniteQuery on **category-sections-query** to warm the first page of products — 4 categories, 4 products each.

Each loader dehydrates its QueryClient into serialized state. On the client, **app-root** wraps everything in QueryClientProvider, and HydrationBoundary rehydrates the cache. TanStack Query hooks read from warm cache on first render — zero waterfalls.
```

### Bad flow narrative

```
When a shopper first navigates to the storefront, the request hits the Node server where react-router-serve picks the matching route. The root-layout-loader fires first, creating a fresh QueryClient and calling prefetchQuery with categories-query options -- this fetches the full category list from dummyjson via the api-client. For the home page, the home-loader goes further: it awaits the categories, then calls prefetchInfiniteQuery on category-sections-query to warm the first page (4 categories, 4 products each). The products-loader does the same for /products, prefetching 8 products. Each loader then dehydrates the QueryClient into serialized state and passes it through useLoaderData. On the client, app-root wraps everything in QueryClientProvider, and each route's HydrationBoundary rehydrates the cache -- so TanStack Query hooks read from warm cache on first render, avoiding a flash of loading state.
```

The bad example is one paragraph, 150+ words, uses `--` not `—`, doesn't bold component names consistently, and buries the key insight (zero waterfalls) at the very end.
