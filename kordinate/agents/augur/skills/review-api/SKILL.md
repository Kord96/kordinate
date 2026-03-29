---
name: review-api
description: Review a project's API surface (REST, GraphQL, gRPC, WebSocket, SSE) — endpoint inventory, convention compliance, gateway pattern adherence, hexagonal architecture checks. Produces a prioritized report.
argument-hint: "<project>"
curated: true
scope: global
---

# review-api

Review a project's API surface against REST conventions (or style-appropriate equivalents for GraphQL, gRPC, WebSocket, SSE), gateway pattern adherence, and hexagonal architecture patterns. Produces a structured report with an endpoint inventory and prioritized findings.

## Arguments

`$ARGUMENTS` -- Required: `<project>` (e.g., `logbd`, `stoik`, or an absolute path like `/tmp/repos/myproject`). If `<project>` is an absolute path, use it directly. Otherwise check `~/<project>/`, `~/repos/<project>/`, `~/test-repos/<project>/`.

## Steps

1. **Parse project name** from `$ARGUMENTS`. If missing, show usage and exit:
   ```
   Usage: /review-api <project>
   Example: /review-api stoik
   ```

2. **Locate the project directory.** If `<project>` is an absolute path, use it directly. Otherwise check `~/<project>/`, then `~/repos/<project>/`, then `~/test-repos/<project>/`. If not found, report and exit.

3. **Detect web framework** -- scan for imports, config files, and dependency manifests. Use the detection tables in `frameworks.md` to identify the framework(s) in use. If unrecognized, fall back to generic route pattern scanning and note the limitation. If multiple frameworks are detected, treat each as a separate API surface.

4. **Discover route definitions** -- find all route/endpoint declarations using the framework-specific route patterns from `frameworks.md`. Build a table: method, path, handler function, file location.

   For each endpoint, also note:
   - **Auth**: does this endpoint have auth middleware, a guard/decorator, or sit behind a default-deny layer? Record `yes`, `no`, `gateway` (if auth is handled externally), or `inherited` (if auth is applied at the router/group level rather than on the handler itself -- e.g., FastAPI `Depends()` on an `APIRouter`, Express `router.use(authMiddleware)`, or NestJS `@UseGuards()` on a controller class).
   - **Validation**: does the handler validate its input (request body, query params) via a schema, decorator, or type annotation? Record `yes`, `no`, or `partial`.

   These columns appear in the Endpoints table in the report.

   **If no endpoints are found:** report this as the primary finding. Check whether the project is a library, uses code generation (OpenAPI, gRPC), or registers routes dynamically. Note what you found and skip steps 5-7 (still write the report -- use "N/A" for Pattern Compliance and omit empty severity sections).

5. **REST hygiene checklist** -- evaluate each concern below. For non-REST API styles (GraphQL, gRPC, WebSocket, SSE), see the "Non-REST API Styles" section for which checks apply and how to adapt them. For each concern, record a finding only if an issue exists -- clean passes do not appear in the report.

   **Severity tie-breaking:** when a finding sits between two levels (e.g., versioning is present in most route groups but missing from one), use the *higher* severity. It is cheaper for the reader to downgrade a finding they disagree with than to discover a real problem was buried at a lower level. If you genuinely cannot decide, state both candidate levels in the finding text and let the reader resolve it (e.g., "RECOMMENDED (arguably MINOR) -- ...").

   **Grouping findings at scale:** when the same issue recurs across many endpoints (e.g., 8 of 30 handlers contain inline DB queries), write one finding that names the pattern and lists the affected files/handlers, rather than 8 separate findings. Include the count (e.g., "8/30 handlers query the DB directly"). Individual findings are for issues that are unique to a single endpoint.

   **Ordering within a severity level:** list findings by scope first (project-wide before localized), then by number of affected endpoints (descending). This puts the highest-leverage fixes at the top.

   | Concern | What to look for | Severity guide |
   |---------|-----------------|----------------|
   | Naming | kebab-case, plural nouns, no verbs in paths (HTTP method expresses the action) | MINOR if inconsistent casing or mixing singular/plural; RECOMMENDED only if verbs in paths create genuine ambiguity about resource identity (e.g., `/getUser` alongside `/users`) |
   | Versioning | `/v1/`, `/v2/`, `api_version` patterns | RECOMMENDED if absent; MINOR if inconsistent |
   | Error format | Global error handler, shared error schema, exception middleware | RECOMMENDED if no global handler; MINOR if formats vary |
   | Auth coverage | Default-deny middleware, per-route auth decorators/guards | CRITICAL if no default-deny layer (unauthenticated-by-default means new routes are exposed); RECOMMENDED if per-route only (each new route must remember to add auth). Health/readiness/liveness endpoints (`/healthz`, `/readyz`, `/livez`, `/health`) are expected to skip auth -- do not flag them. |
   | Rate limiting | Rate limiter middleware or decorators on unauthenticated/public-facing endpoints | RECOMMENDED if absent on public endpoints; not required on internal-only services |
   | Auth consistency | Multiple auth mechanisms (API keys, OAuth, session cookies, JWTs) across the same API surface | MINOR if multiple mechanisms coexist with clear per-route intent (e.g., public API uses keys, admin panel uses sessions); RECOMMENDED if the choice appears accidental or undocumented, since inconsistent auth strategies complicate security audits |
   | Validation | Pydantic, marshmallow, Zod, JSON schema, or framework-native validation at the API boundary | CRITICAL if absent AND unvalidated input reaches DB queries or shell commands (injection risk); RECOMMENDED if absent otherwise; MINOR if inconsistent |
   | Method correctness | POST used for read-only operations (listing, querying, searching). REST convention: GET for reads, POST for creates. POST-for-read is acceptable when request bodies are complex (filter objects), but should use a consistent pattern (e.g., all list endpoints use POST, or none do). | MINOR if POST-for-read is consistent across all list endpoints with a documented reason (e.g., complex filter bodies); RECOMMENDED if mixed (some lists use GET, some use POST) or if simple queries that could be GET params use POST instead |
   | Health endpoints | `/health`, `/healthz`, `/readyz`, `/livez`, `/ready`, `/live` or equivalent health/readiness checks | RECOMMENDED if absent on a long-running server (production deployments need health probes for orchestrators like k8s); not applicable for CLI tools, libraries, or serverless functions |
   | Pagination | Consistent pagination on list endpoints -- offset/limit, cursor-based, or page-based | MINOR if inconsistent across list endpoints; not a finding if pagination is consistent or if there are no list endpoints |

6. **Gateway pattern compliance** -- route handlers should delegate to a service or use-case layer, not contain business logic.

   The API layer is an *adapter*: it translates HTTP into domain calls and domain results back into HTTP. When business logic leaks into handlers, that logic cannot be reused from other entry points (CLI, message queue, scheduled jobs), and testing suffers -- HTTP integration tests replace what should be pure domain unit tests.

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

   Partial vs non-compliant: if a service layer exists and the *majority* of handlers use it, but some bypass it, the pattern status is **partial**. If no service layer exists, or most handlers bypass it, the status is **non-compliant**. Use the same threshold for hexagonal compliance in step 7.

   **External API gateway note:** if the project sits behind a gateway (Kong, AWS API Gateway, Traefik, nginx with auth_request), note it in the Pattern Compliance section. If the app relies *entirely* on the gateway for auth or rate limiting with no application-level fallback, also add a RECOMMENDED finding to the Findings section (coupling risk -- protections vanish if the gateway is bypassed during development or testing). Mere redundancy (app re-checks what the gateway already handles) is not a finding.

7. **Hexagonal architecture compliance** -- handlers should not import infrastructure modules directly.

   Hexagonal architecture keeps the domain independent of delivery mechanisms and infrastructure. When a handler imports a database driver or external SDK directly, the API layer is coupled to specific infrastructure choices, making database changes, service swaps, and isolated testing all harder.

   Signals of coupling in handler files:
   - Database driver imports (`sqlalchemy`, `psycopg2`, `mongoose`, `pgx`, `database/sql`)
   - Database query DSL imports (`sqlalchemy.func`, `sqlalchemy.select`, `sqlalchemy.and_`, `sqlalchemy.or_`, `sqlalchemy.insert`, `sqlalchemy.update`, `sqlalchemy.delete`) -- these are a stronger signal than driver imports because they indicate the handler is constructing queries, not just passing a session to a service layer
   - ORM model imports used for direct queries (`Model.objects.filter`, `Session.query(Model)`) -- handler files importing models to query is a sign the handler *is* the service layer
   - External service SDK imports (`boto3`, `stripe`, `aws-sdk`, `@google-cloud/*`, `azure-*`)
   - Message broker client imports (`pika`, `kafka-python`, `amqplib`, `bullmq`, `aio-pika`)
   - Email/notification library imports (`smtplib`, `nodemailer`, `sendgrid`, `twilio`)
   - Cache client imports (`redis`, `ioredis`, `memcached`, `cachetools`)
   - Infrastructure utility imports (queue producers, file storage clients)

   Clean counterexamples (what properly decoupled handlers import instead):
   - `services/`, `usecases/`, `domain/`, or `ports/` modules
   - Abstract repository or gateway interfaces, not concrete implementations

   Scoring:
   - CRITICAL if handler files import DB drivers, external SDKs, or infra modules directly (no port/adapter indirection exists)
   - RECOMMENDED if port/adapter structure exists but some handler files bypass it

8. **Write the report** to `<project-repo>/.kord/agents/augur/memory/api-review.md` using the template in [Output](#output). Create the directory if it does not exist. Delegate to scribe if guard-md blocks.

9. **Report** -- summarize findings to the caller: framework detected, endpoint count, critical/recommended/minor counts, and the path where the full report was written.

## Non-REST API Styles

Some projects expose APIs that are not conventional REST. Adapt the review as follows:

- **GraphQL**: look for schema files (`.graphql`, `schema.gql`) and resolver definitions. The endpoint inventory becomes a resolver inventory (query/mutation/subscription, resolver function, file). REST naming rules do not apply, but auth coverage (per-resolver or schema-level), validation (input types), gateway pattern (resolvers should delegate to services), and hexagonal checks all still apply.
- **gRPC**: look for `.proto` files and generated server stubs. The endpoint inventory becomes a service/method inventory. REST naming and versioning checks do not apply. Auth (interceptors/middleware), gateway pattern (handlers should delegate), and hexagonal checks still apply. Note the proto package version as the versioning mechanism.
- **WebSocket**: look for WebSocket upgrade handlers, socket.io event registrations, or WS route definitions. Inventory the event names and handlers. Auth (connection-level auth/handshake), validation (message schema), and gateway/hexagonal checks all apply. Note that WebSocket endpoints often lack the per-message auth that REST gets from per-request middleware -- flag this as RECOMMENDED if event handlers assume auth from the initial handshake without per-message authorization for sensitive operations (e.g., a `delete_resource` event that trusts the connection-level identity without checking current permissions -- the user's role may have changed since the handshake).
- **SSE (Server-Sent Events)**: look for `text/event-stream` content types, `EventSource` references, or SSE helper libraries. Inventory the SSE endpoints. Auth (initial connection auth), validation (query params that control the stream), and gateway/hexagonal checks apply. SSE connections are long-lived -- flag as RECOMMENDED if there is no mechanism to revoke or timeout stale connections (a user who loses auth mid-stream continues receiving events).

If the project is purely one of these styles, skip inapplicable REST hygiene checks and note the API style in the Framework section of the report. If the project mixes REST with one of these, treat each style as a separate API surface.

## Output

Report template for `<project-repo>/.kord/agents/augur/memory/api-review.md`:

```markdown
# <project> -- API Review

> Auto-generated by /augur:review-api. Last run: <YYYY-MM-DD>

## Framework

<detected framework(s) and version(s), or "unrecognized -- best-effort scan" if applicable>
<API style: REST | GraphQL | gRPC | WebSocket | SSE | mixed (list styles). Omit for plain REST.>

## Summary

<total endpoint count> endpoints across <API style(s)>. <CRITICAL count> critical, <RECOMMENDED count> recommended, <MINOR count> minor findings.

## Endpoints

| Method | Path | Handler | File | Auth | Validation |
|--------|------|---------|------|------|------------|
| GET | /v1/users | list_users | src/api/users.py:15 | inherited | yes |
| POST | /v1/users | create_user | src/api/users.py:34 | gateway | partial |
| GET | /healthz | healthcheck | src/api/health.py:5 | no (expected) | no |
| ... | ... | ... | ... | ... | ... |

<If no endpoints found, state that clearly and explain why (library, codegen, dynamic routes).>

## Findings

### CRITICAL
- <finding with file:line reference and explanation>

### RECOMMENDED
- <finding with file:line reference and explanation>

### MINOR
- <finding with file:line reference and explanation>

<Omit any severity section that has no findings.>

## Pattern Compliance

| Pattern | Status | Notes |
|---------|--------|-------|
| API Gateway | compliant / partial / non-compliant | <explanation of what was found> |
| Hexagonal | compliant / partial / non-compliant | <explanation of what was found> |

<If an external API gateway was detected, note it here with observations about duplicated or delegated concerns.>

## Notes

<Optional. Cross-cutting observations that do not fit a specific finding or pattern: architectural strengths worth preserving, conventions the team follows well, testing observations, or context that would help a future reviewer. Keep brief -- 2-5 bullet points max. Omit this section entirely if there is nothing noteworthy beyond the findings above.>
```
