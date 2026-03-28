---
description: Error Boundary — component-level error catching and fallback rendering
type: pattern
curated: true
scope: global
preloaded: none
graphable: true
abstraction: [frontend, error-handling]
---
# Error Boundary

## Recognition

How to identify this pattern in code.

### Signatures

- `ErrorBoundary` class component with `componentDidCatch` and `getDerivedStateFromError` (React)
- `react-error-boundary` library with `ErrorBoundary` component, `fallbackRender`, `useErrorBoundary`
- `onErrorCaptured` lifecycle hook in parent components (Vue)
- `ErrorHandler` class or `APP_INITIALIZER` with global error handling (Angular)
- `handleError` hook in `hooks.client.ts` or `+error.svelte` pages (SvelteKit)
- `errorElement` property on route definitions (React Router)
- `<Suspense>` with `fallback` combined with error boundaries for async error handling
- `fallback` or `FallbackComponent` props on boundary components
- `resetErrorBoundary` or retry mechanisms allowing recovery from errors
- Per-route `+error.svelte`, `error.tsx`, or `error.vue` files in file-based routing

### Confidence

- **high** -- Dedicated error boundary component wrapping a subtree with explicit fallback UI, error logging, and recovery mechanism
- **medium** -- Try/catch in render logic or lifecycle hooks that sets local error state and conditionally renders an error message
- **low** -- Global `window.onerror` or `unhandledrejection` handler that logs but does not provide component-level recovery

## Architecture

Look for a component boundary that intercepts rendering errors in its subtree, displays fallback UI, and optionally supports recovery or error reporting.

### Review Checklist

- Error boundaries are placed at meaningful subtree boundaries (per route, per feature section) not just at the root
- Fallback UI communicates the error clearly and offers a recovery action (retry, navigate away)
- Caught errors are reported to an error tracking service (Sentry, Datadog, etc.)
- Boundaries do not swallow errors silently -- logging or reporting always accompanies the catch
- Async errors (promise rejections, data fetching) are handled in addition to synchronous render errors
- Nested boundaries allow granular degradation without taking down the entire page

### Anti-patterns

- A single root-level error boundary that shows a generic error page for any failure anywhere
- Fallback UI that provides no recovery path, forcing the user to reload the entire application
- Error boundaries that catch and hide errors without reporting them to monitoring
- Using error boundaries to handle expected control flow (form validation, empty states) instead of exceptional failures
- No error boundary at all, letting uncaught errors crash the entire React tree to a white screen
