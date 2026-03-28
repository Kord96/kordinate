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

**Severity tie-breaking:** when a finding sits between two levels, use the *higher* severity.

**Grouping findings at scale:** when the same issue recurs across many endpoints, write one finding that lists the affected files/handlers and includes the count (e.g., "8/30 handlers query the DB directly").

**Ordering within severity:** list findings by scope first (project-wide before localized), then by number of affected endpoints (descending).

| Concern | What to look for | Severity guide |
|---------|-----------------|----------------|
| Naming | kebab-case, plural nouns, no verbs in paths | MINOR if inconsistent casing or mixing singular/plural; RECOMMENDED only if verbs create genuine ambiguity |
| Versioning | `/v1/`, `/v2/`, `api_version` patterns | RECOMMENDED if absent; MINOR if inconsistent |
| Error format | Global error handler, shared error schema, exception middleware | RECOMMENDED if no global handler; MINOR if formats vary |
| Auth coverage | Default-deny middleware, per-route auth decorators/guards | CRITICAL if no default-deny layer; RECOMMENDED if per-route only. Health/readiness endpoints (`/healthz`, `/readyz`, `/livez`, `/health`) are expected to skip auth |
| Rate limiting | Rate limiter middleware or decorators on unauthenticated/public-facing endpoints | RECOMMENDED if absent on public endpoints; not required on internal-only services |
| Auth consistency | Multiple auth mechanisms across the same API surface | MINOR if coexist with clear intent; RECOMMENDED if accidental or undocumented |
| Validation | Pydantic, marshmallow, Zod, JSON schema, or framework-native validation | CRITICAL if absent AND unvalidated input reaches DB queries or shell commands; RECOMMENDED if absent otherwise; MINOR if inconsistent |

## Gateway Pattern Compliance

Route handlers should delegate to a service or use-case layer, not contain business logic. The API layer is an *adapter*: it translates HTTP into domain calls and domain results back into HTTP.

Signals of leakage in route handlers:
- Direct database queries (ORM calls, raw SQL, connection usage)
- Complex conditional logic or multi-step orchestration
- Domain calculations or business rule enforcement
- Direct calls to external services (HTTP clients, queue producers, email/SMS senders)
- File system operations driven by request input
- Inline session or token management logic
- Manual response body construction beyond simple serialization
- Direct cache operations (Redis/Memcached get/set in handlers)
- Transaction management (explicit BEGIN/COMMIT/ROLLBACK on handlers)

Scoring:
- CRITICAL if handlers are the primary location for DB queries, domain logic, or external service calls (no service layer exists)
- RECOMMENDED if a service layer exists but some handlers bypass it

**External API gateway note:** if the project sits behind a gateway (Kong, AWS API Gateway, Traefik, nginx with auth_request), note it. If the app relies *entirely* on the gateway with no application-level fallback, add a RECOMMENDED finding (coupling risk).

## Hexagonal Architecture Compliance

Handlers should not import infrastructure modules directly.

Signals of coupling in handler files:
- Database driver imports (`sqlalchemy`, `psycopg2`, `mongoose`, `pgx`, `database/sql`)
- ORM model imports used for direct queries
- External service SDK imports (`boto3`, `stripe`, `aws-sdk`, `@google-cloud/*`)
- Message broker client imports (`pika`, `kafka-python`, `amqplib`, `bullmq`)
- Email/notification library imports
- Cache client imports (`redis`, `ioredis`, `memcached`)
- Infrastructure utility imports

Clean counterexamples (what properly decoupled handlers import instead):
- `services/`, `usecases/`, `domain/`, or `ports/` modules
- Abstract repository or gateway interfaces

Scoring:
- CRITICAL if handler files import DB drivers, external SDKs, or infra modules directly
- RECOMMENDED if port/adapter structure exists but some handler files bypass it

## Non-REST API Styles

- **GraphQL**: schema files (`.graphql`, `schema.gql`) and resolver definitions. Endpoint inventory becomes resolver inventory. Auth (per-resolver or schema-level), validation (input types), gateway and hexagonal checks apply. REST naming rules do not apply.
- **gRPC**: `.proto` files and generated server stubs. Endpoint inventory becomes service/method inventory. Auth (interceptors/middleware), gateway and hexagonal checks apply. Proto package version is the versioning mechanism.
- **WebSocket**: WebSocket upgrade handlers, socket.io event registrations, WS route definitions. Auth (connection-level), validation (message schema), gateway/hexagonal checks apply. Flag RECOMMENDED if event handlers assume auth from handshake without per-message authorization for sensitive operations.
- **SSE**: `text/event-stream` content types, `EventSource` references, SSE helpers. Auth (initial connection), validation (query params), gateway/hexagonal checks apply. Flag RECOMMENDED if no mechanism to revoke/timeout stale connections.

If the project mixes REST with one of these, treat each as a separate API surface.
