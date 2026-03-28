---
description: Middleware — request/response pipeline interceptors for cross-cutting concerns
type: pattern
curated: true
scope: global
preloaded: none
graphable: true
abstraction: [integration, lifecycle]
---
# Middleware

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
