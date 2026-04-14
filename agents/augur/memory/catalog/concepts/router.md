---
description: Router — frontend URL-based navigation and view switching
type: pattern
graphable: true
abstraction: [frontend, integration]
status: primary
scope: frontend
relationships:
  related_to: [server-route-registration, route-guard]
---
# Router

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
