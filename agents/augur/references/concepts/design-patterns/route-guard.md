---
kind: concept
name: route-guard
signatures:
  concept: route-guard
  positive:
    strong:
    - framework navigation guard API with redirect
    - auth or permission checks in route middleware
    medium:
    - protected route wrapper components
    weak:
    - ad-hoc navigation checks after render
  negative:
  - content renders before redirect
  - auth checks only in page component lifecycle hooks
  notes:
  - This is a guard concept, not merely the presence of auth code near routes.
source:
  memory_concept: memory/catalog/concepts/route-guard.md
type: pattern
abstraction:
- frontend
- security
scope: frontend
status: specialized
review_questions:
  threshold: 5
  entries:
  - id: route-guard-pre-render
    prompt: Does the guard block navigation before protected content renders?
    weight: 3
    signals:
    - redirect(
    - CanActivate
    - middleware.ts
  - id: route-guard-auth-check
    prompt: Does the guard evaluate auth or permissions rather than only client-side
      state toggles?
    weight: 2
    signals:
    - isAuthenticated
    - hasRole
    - permission
monitoring:
  applies_to:
  - flow
  - component
  health_signals:
  - name: authorization.denied.rate
    description: Rate of requests denied by route guards or authorization middleware.
  - name: route_guard.error.rate
    description: Failures inside guard logic that can block or misroute requests.
  business_metrics: []
  gaps:
  - Missing deny-rate and guard-error metrics makes it hard to distinguish policy
    enforcement from auth regressions.
---

# Explanation

## Recognition

How to identify this pattern in code.

### Signatures

- `clientLoader` or `loader` returning `redirect()` based on auth state (React Router)
- `beforeRouteEnter`, `beforeEach`, `beforeRouteLeave` navigation guards (Vue Router)
- `CanActivate`, `CanDeactivate`, `CanLoad` guard interfaces and `canActivate` route property (Angular)
- `handle` hook in `hooks.server.ts` checking session before resolving (SvelteKit)
- `middleware/` directory with named middleware functions checking auth (Nuxt)
- Next.js `middleware.ts` with `NextResponse.redirect` or `NextResponse.rewrite`
- Higher-order components or wrapper components checking auth state and redirecting (`<ProtectedRoute>`, `<AuthGuard>`)
- Token or session checks before allowing navigation: `isAuthenticated`, `hasRole`, `checkPermission`
- Redirect to login page with return URL parameter on guard failure

### Confidence

- **high** -- Framework navigation guard API (beforeEach, CanActivate, middleware) with explicit auth check, role verification, and redirect on failure
- **medium** -- Wrapper component or layout that conditionally renders children based on auth state, with redirect side effect
- **low** -- Ad-hoc auth check inside a page component's mount lifecycle that navigates away on failure

## Architecture

Look for a centralized or per-route gate that evaluates access conditions before rendering the target view, with well-defined redirect behavior on denial.

### Relationship To Other Concepts

- `route-guard` is a specialized routing concern, not the primary routing concept.
- Prefer [router](/concepts/router) for the navigation system itself.
- Prefer `route-guard` when the main architectural concern is pre-render authorization or navigation gating.

### Review Checklist

- Guard logic is centralized or composable, not duplicated across individual page components
- Auth state is checked against a reliable source (token validation, session API) not just local storage
- Failed guards redirect to an appropriate destination (login page, 403 page) with return URL preserved
- Guards handle loading/pending auth state gracefully (show loading, not flash of protected content)
- Role and permission checks are granular enough for the application's access model
- Guards cover both initial page load and client-side navigation

### Anti-patterns

- Checking auth only on client-side navigation but not on direct URL access (server-side gap)
- Flash of protected content before the guard redirects (guard runs after render, not before)
- Hardcoded role strings scattered across guard implementations instead of a permissions abstraction
- Guards that silently fail, leaving the user on a broken or empty page instead of redirecting
- Duplicating guard logic in every page component instead of using route-level or layout-level guards

### Boundary

Use `route-guard` when the code conditionally allows or redirects frontend navigation before a route is entered.

Do not use it for backend authorization middleware or API gateway checks unless the guarded boundary is frontend route navigation.
