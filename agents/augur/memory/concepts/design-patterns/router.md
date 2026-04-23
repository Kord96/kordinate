---
kind: concept
name: router
signatures:
  concept: router
  positive:
    strong:
    - framework router library with route definitions
    - declarative path-to-view mapping
    medium:
    - navigation helpers and route parameters around a routing setup
    weak:
    - manual location checks or pushState calls
  negative:
  - URL-based conditionals without a coherent routing system
  notes:
  - Keep this separate from backend API route extraction.
  - Use this concept for UI navigation routers, not server route registration.
type: pattern
abstraction:
- frontend
- integration
scope: frontend
status: primary
review_questions:
  threshold: 4
  entries:
  - id: router-declarative-map
    prompt: Is there a declarative mapping from paths to views or components in the
      UI navigation layer?
    weight: 2
    signals:
    - BrowserRouter
    - Route
    - RouterView
  - id: router-navigation-and-params
    prompt: Are navigation helpers or route parameters used as part of the frontend
      routing system?
    weight: 2
    signals:
    - useNavigate
    - useParams
    - router.push
monitoring:
  applies_to:
  - component
  health_signals:
  - name: navigation.transition.latency
    description: End-to-end latency for client-side route transitions.
  - name: navigation.not_found.rate
    description: Frequency of unmatched navigation paths or fallback route hits.
  business_metrics: []
  gaps:
  - Missing navigation latency and fallback-route metrics hides drift in the UI routing
    layer.
family: design-patterns
---

# Explanation

This concept is for frontend or UI navigation routing.

- Use it when URLs or navigation state select views, screens, or UI trees.
- Do not use it for backend route declaration; use [server-route-registration](/concepts/server-route-registration) for that.

## Recognition

How to identify this pattern in code.

### Signatures

- `react-router-dom` with `BrowserRouter`, `Routes`, `Route`, `useNavigate`, `useParams` (React)
- `vue-router` with `createRouter`, `RouterView`, `RouterLink`, `useRoute`, `useRouter` (Vue)
- `@angular/router` with `RouterModule`, `ActivatedRoute`, `Router`, route configuration arrays (Angular)
- SvelteKit file-based routing with `+page.svelte`, `+layout.svelte`, `$app/navigation` imports
- `next/router` or `next/navigation` with `useRouter`, `usePathname`, `useSearchParams` (Next.js)
- Nuxt file-based routing with `pages/` directory convention, `NuxtLink`, `navigateTo`
- Route definition objects with `path`, `element`/`component`, `children` properties
- Path parameters (`:id`, `[id]`, `{id}`), wildcard routes, catch-all segments
- Nested route configurations with `Outlet`, `RouterView`, or `router-outlet` placeholders
- Programmatic navigation: `navigate()`, `router.push()`, `router.navigate()`

This concept is for frontend or UI-navigation routers.
Backend API route registration belongs in deterministic `routes` facts, not this concept.

### Confidence

- **high** -- Framework router library imported with route definitions mapping URL paths to components, navigation hooks, and parameter extraction
- **medium** -- URL-based conditional rendering that switches displayed content based on `window.location` or hash fragments, but without a formal router library
- **low** -- Manual `history.pushState` or hash-change listeners that update view state without structured route definitions

## Architecture

Look for a declarative mapping between URL paths and component trees, with support for nested layouts, parameter extraction, and programmatic navigation.

### Review Checklist

- Routes are defined declaratively in a central configuration, not scattered across components
- Nested routes use layout components to avoid re-rendering shared UI on navigation
- Route parameters are validated or typed before use in data fetching
- Navigation guards or loaders handle auth checks and data prefetching before rendering
- 404 and error routes are explicitly defined with appropriate fallback UI
- Code splitting is applied per route to avoid loading the entire app upfront

### Anti-patterns

- Defining routes inline across multiple files with no central route manifest
- Fetching data inside components after mount instead of using route-level loaders or guards
- Using string concatenation to build URLs instead of typed route helpers or path utilities
- Nested routes that re-fetch parent data because layout boundaries are not configured
- Catch-all routes that silently swallow navigation errors instead of showing meaningful feedback

### Relationship To Other Concepts

- Related to [server-route-registration](/concepts/server-route-registration) because this concept commonly appears alongside it or is clarified by contrast with it.
- Related to [route-guard](/concepts/route-guard) because this concept commonly appears alongside it or is clarified by contrast with it.

### Boundary

Use `router` when the important observation is this specific architectural concern within a frontend, UI, or client-side architectural concern.

Do not use it just because a few signatures match; the surrounding responsibilities and architectural role should line up too.
