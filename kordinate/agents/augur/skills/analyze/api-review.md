# API Surface Review

Level 3 resource for the architect skill. Referenced from step 4 (review API surface). Carries the full API review procedure.

## Framework Detection

Use the framework detection tables in [frameworks.md](frameworks.md) to identify the framework(s) in use. If unrecognized, fall back to generic route pattern scanning. If multiple frameworks are detected, treat each as a separate API surface.

## Route Discovery

Find all route/endpoint declarations using framework-specific route patterns from [frameworks.md](frameworks.md). For each endpoint, capture:

- **Method**: GET, POST, PUT, DELETE, PATCH, etc.
- **Path**: the route pattern
- **Handler**: function/method name
- **File**: source file and line number
- **Auth**: `yes` (explicit auth on this handler), `no` (no auth), `gateway` (auth handled externally), `inherited` (auth applied at router/group level — e.g., FastAPI `Depends()` on an `APIRouter`, Express `router.use(authMiddleware)`, NestJS `@UseGuards()` on a controller class)
- **Validation**: `yes` (schema/decorator/type annotation validates input), `no`, `partial`

**If no endpoints found:** check whether the project is a library, uses code generation (OpenAPI, gRPC), or registers routes dynamically. Skip the hygiene checklist and compliance checks. Note what was found.

## REST Hygiene Checklist

Evaluate each concern below. Record a finding only if an issue exists — clean passes do not appear in findings.

**Severity tie-breaking:** when a finding sits between two levels (e.g., versioning is present in most route groups but missing from one), use the *higher* severity. It is cheaper for the reader to downgrade a finding they disagree with than to discover a real problem was buried at a lower level. If you genuinely cannot decide, state both candidate levels in the finding text (e.g., "RECOMMENDED (arguably MINOR) — ...").

**Grouping findings at scale:** when the same issue recurs across many endpoints (e.g., 8 of 30 handlers contain inline DB queries), write one finding that names the pattern and lists the affected files/handlers, rather than 8 separate findings. Include the count (e.g., "8/30 handlers query the DB directly"). Individual findings are for issues that are unique to a single endpoint.

**Ordering within severity:** list findings by scope first (project-wide before localized), then by number of affected endpoints (descending). This puts the highest-leverage fixes at the top.

| Concern | What to look for | Severity guide |
|---------|-----------------|----------------|
| Naming | kebab-case, plural nouns, no verbs in paths (HTTP method expresses the action) | MINOR if inconsistent casing or mixing singular/plural; RECOMMENDED only if verbs in paths create genuine ambiguity about resource identity (e.g., `/getUser` alongside `/users`) |
| Versioning | `/v1/`, `/v2/`, `api_version` patterns | RECOMMENDED if absent; MINOR if inconsistent |
| Error format | Global error handler, shared error schema, exception middleware | RECOMMENDED if no global handler; MINOR if formats vary |
| Auth coverage | Default-deny middleware, per-route auth decorators/guards | CRITICAL if no default-deny layer (unauthenticated-by-default means new routes are exposed); RECOMMENDED if per-route only (each new route must remember to add auth). Health/readiness/liveness endpoints (`/healthz`, `/readyz`, `/livez`, `/health`) are expected to skip auth — do not flag them |
| Rate limiting | Rate limiter middleware or decorators on unauthenticated/public-facing endpoints | RECOMMENDED if absent on public endpoints; not required on internal-only services |
| Auth consistency | Multiple auth mechanisms (API keys, OAuth, session cookies, JWTs) across the same API surface | MINOR if multiple mechanisms coexist with clear per-route intent (e.g., public API uses keys, admin panel uses sessions); RECOMMENDED if the choice appears accidental or undocumented, since inconsistent auth strategies complicate security audits |
| Validation | Pydantic, marshmallow, Zod, JSON schema, or framework-native validation at the API boundary | CRITICAL if absent AND unvalidated input reaches DB queries or shell commands (injection risk); RECOMMENDED if absent otherwise; MINOR if inconsistent |

## Gateway Pattern Compliance

Route handlers should delegate to a service or use-case layer, not contain business logic. The API layer is an *adapter*: it translates HTTP into domain calls and domain results back into HTTP. When business logic leaks into handlers, that logic cannot be reused from other entry points (CLI, message queue, scheduled jobs), and testing suffers — HTTP integration tests replace what should be pure domain unit tests.

Signals of leakage in route handlers:
- Direct database queries (ORM calls, raw SQL, connection usage)
- Complex conditional logic or multi-step orchestration
- Domain calculations or business rule enforcement
- Direct calls to external services (HTTP clients, queue producers, email/SMS senders)
- File system operations driven by request input (reading/writing files, uploads without a storage abstraction)
- Inline session or token management logic (JWT signing, session store writes)
- Manual response body construction beyond simple serialization (building nested dicts/objects with business meaning)
- Direct cache operations (Redis/Memcached get/set calls in handlers instead of through a service or caching decorator)
- Transaction management (explicit BEGIN/COMMIT/ROLLBACK or `@transaction` decorators on handlers rather than service methods)

Scoring:
- CRITICAL if handlers are the primary location for DB queries, domain logic, or external service calls (no service layer exists, or it is bypassed)
- RECOMMENDED if a service layer exists but some handlers bypass it with inline logic

**Partial vs non-compliant:** if a service layer exists and the *majority* of handlers use it, but some bypass it, the pattern status is **partial**. If no service layer exists, or most handlers bypass it, the status is **non-compliant**. Use the same threshold for hexagonal compliance below.

**External API gateway note:** if the project sits behind a gateway (Kong, AWS API Gateway, Traefik, nginx with auth_request), note it in the compliance section. If the app relies *entirely* on the gateway for auth or rate limiting with no application-level fallback, add a RECOMMENDED finding (coupling risk — protections vanish if the gateway is bypassed during development or testing). Mere redundancy (app re-checks what the gateway already handles) is not a finding.

## Hexagonal Architecture Compliance

Handlers should not import infrastructure modules directly. Hexagonal architecture keeps the domain independent of delivery mechanisms and infrastructure. When a handler imports a database driver or external SDK directly, the API layer is coupled to specific infrastructure choices, making database changes, service swaps, and isolated testing all harder.

Signals of coupling in handler files:
- Database driver imports (`sqlalchemy`, `psycopg2`, `mongoose`, `pgx`, `database/sql`)
- ORM model imports used for direct queries (`Model.objects.filter`, `Session.query(Model)`) — handler files importing models to query is a sign the handler *is* the service layer
- External service SDK imports (`boto3`, `stripe`, `aws-sdk`, `@google-cloud/*`, `azure-*`)
- Message broker client imports (`pika`, `kafka-python`, `amqplib`, `bullmq`, `aio-pika`)
- Email/notification library imports (`smtplib`, `nodemailer`, `sendgrid`, `twilio`)
- Cache client imports (`redis`, `ioredis`, `memcached`, `cachetools`)
- Infrastructure utility imports (queue producers, file storage clients)

Clean counterexamples (what properly decoupled handlers import instead):
- `services/`, `usecases/`, `domain/`, or `ports/` modules
- Abstract repository or gateway interfaces

Scoring:
- CRITICAL if handler files import DB drivers, external SDKs, or infra modules directly
- RECOMMENDED if port/adapter structure exists but some handler files bypass it

## Non-REST API Styles

- **GraphQL**: look for schema files (`.graphql`, `schema.gql`) and resolver definitions. The endpoint inventory becomes a resolver inventory (query/mutation/subscription, resolver function, file). REST naming rules do not apply, but auth coverage (per-resolver or schema-level), validation (input types), gateway pattern (resolvers should delegate to services), and hexagonal checks all still apply.
- **gRPC**: look for `.proto` files and generated server stubs. The endpoint inventory becomes a service/method inventory. REST naming and versioning checks do not apply. Auth (interceptors/middleware), gateway pattern (handlers should delegate), and hexagonal checks still apply. Note the proto package version as the versioning mechanism.
- **WebSocket**: look for WebSocket upgrade handlers, socket.io event registrations, or WS route definitions. Inventory the event names and handlers. Auth (connection-level auth/handshake), validation (message schema), and gateway/hexagonal checks all apply. Flag RECOMMENDED if event handlers assume auth from the initial handshake without per-message authorization for sensitive operations (e.g., a `delete_resource` event that trusts the connection-level identity without checking current permissions — the user's role may have changed since the handshake).
- **SSE (Server-Sent Events)**: look for `text/event-stream` content types, `EventSource` references, or SSE helper libraries. Inventory the SSE endpoints. Auth (initial connection auth), validation (query params that control the stream), and gateway/hexagonal checks apply. SSE connections are long-lived — flag RECOMMENDED if there is no mechanism to revoke or timeout stale connections (a user who loses auth mid-stream continues receiving events).

If the project is purely one of these styles, skip inapplicable REST hygiene checks. If the project mixes REST with one of these, treat each style as a separate API surface.
