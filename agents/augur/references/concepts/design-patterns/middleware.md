---
kind: concept
name: middleware
signatures:
  concept: middleware
  positive:
    strong:
    - framework middleware registration plus next-stage forwarding
    - ordered request or action pipeline around handlers
    medium:
    - interceptors or hook pipelines implementing cross-cutting concerns
    weak:
    - decorators or wrappers that add behavior without a shared pipeline contract
  negative:
  - business-logic handlers mislabeled as middleware
  - one-off wrappers with no composable stage sequencing
  notes:
  - Middleware is a pipeline shape, not a specific concern like auth or rate limiting.
source:
  memory_concept: memory/catalog/concepts/middleware.md
type: pattern
abstraction:
- integration
- lifecycle
scope: cross-cutting
status: primary
review_questions:
  threshold: 5
  entries:
  - id: middleware-pipeline
    prompt: Is there a composable request or action pipeline where each stage forwards
      control to the next?
    weight: 3
    signals:
    - app.use
    - middleware
    - next(
  - id: middleware-cross-cutting
    prompt: Does the middleware implement cross-cutting concerns such as auth, logging,
      or rate limiting rather than core business logic?
    weight: 2
    signals:
    - BaseHTTPMiddleware
    - canActivate
    - interceptor
monitoring:
  applies_to:
  - component
  - flow
  health_signals:
  - name: middleware.error.rate
    description: Failures in request-pipeline stages before the main handler runs.
  - name: middleware.short_circuit.rate
    description: Requests terminated early by auth, validation, rate-limit, or redirect
      middleware.
  business_metrics: []
  gaps:
  - Missing stage-level visibility makes ordering and short-circuit bugs hard to debug.
---

# Explanation

## Recognition

How to identify this pattern in code.

### Signatures

- `app.use()` with function signature `(req, res, next)` (Express)
- `middleware.ts` or `middleware.js` at project root with `NextRequest`/`NextResponse` (Next.js)
- `defineNuxtRouteMiddleware` or files in `middleware/` directory (Nuxt)
- Django `MIDDLEWARE` setting with classes implementing `__call__` or `process_request`/`process_response`
- FastAPI/Starlette `@app.middleware("http")` or `BaseHTTPMiddleware` subclass
- Koa middleware with `async (ctx, next)` signature and `app.use()`
- `@Injectable()` with `NestMiddleware` interface implementing `use(req, res, next)` (NestJS)
- Redux middleware with `store => next => action` curried signature
- Axios interceptors: `axios.interceptors.request.use()`, `axios.interceptors.response.use()`
- ASP.NET `IMiddleware` or `app.Use()` / `app.UseMiddleware<T>()`
- Pipeline ordering: middleware registered in sequence with explicit ordering dependency

### Confidence

- **high** -- Framework middleware API with `next()` call forwarding to the next handler in a pipeline, registered via `app.use()` or configuration array
- **medium** -- Interceptor or hook that wraps requests/responses with cross-cutting logic but is not called "middleware" or does not use a formal pipeline API
- **low** -- Decorator or wrapper function that adds behavior around a handler but without a composable pipeline or `next()` mechanism

## Architecture

Look for a composable pipeline of handlers that each process a request or action, optionally transform it, and forward to the next handler in the chain.

### Relationship To Other Concepts

- `middleware` is a request or action pipeline pattern.
- It commonly enforces cross-cutting concerns around a `rest`, `graphql`, or server route surface.
- It often surrounds a `layered` core but is not the same thing as layering.

### Review Checklist

- Middleware execution order is intentional and documented (auth before route handlers, logging early, error handling last)
- Each middleware has a single cross-cutting concern (not combining auth + logging + rate limiting in one)
- `next()` is always called or the response is explicitly terminated -- no silent drops
- Error-handling middleware is placed at the end of the pipeline to catch upstream failures
- Middleware does not mutate shared state in a way that creates coupling between unrelated middleware
- Performance-sensitive middleware (rate limiting, caching) is placed early to short-circuit expensive downstream work

### Anti-patterns

- Middleware that swallows errors without calling next(err) or returning an error response
- Ordering-dependent middleware with no documentation about why the order matters
- God middleware that handles auth, logging, validation, and transformation in a single function
- Middleware that modifies the request/response object in ways that downstream handlers do not expect
- Applying middleware globally when it is only needed on specific routes or endpoints

### Boundary

Use `middleware` when request or response handling is organized as an intercepting pipeline of cross-cutting steps around a downstream handler.

Do not use it for any helper called before a handler. The important signal is a composable interception chain that wraps request handling.
