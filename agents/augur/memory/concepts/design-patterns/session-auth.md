---
kind: concept
name: session-auth
signatures:
  concept: session-auth
  positive:
    strong:
    - server-side session middleware plus cookie-based session identifiers
    - session lifecycle controls such as regeneration and destruction
    medium:
    - request-scoped session access with a recognizable session store
    weak:
    - signed cookies that may or may not back onto server state
  negative:
  - stateless bearer-token auth mislabeled as session auth
  - local cookie checks with no server-side session store
  notes:
  - Session auth is about server-owned auth state, not merely cookies.
type: pattern
abstraction:
- security
scope: backend
status: primary
review_questions:
  threshold: 5
  entries:
  - id: session-auth-server-state
    prompt: Does the system keep authenticated session state on the server side and
      reference it via cookies or session IDs?
    weight: 3
    signals:
    - req.session
    - request.session
    - express-session
  - id: session-auth-cookie-controls
    prompt: Are secure cookie and session-lifecycle controls part of the auth design?
    weight: 2
    signals:
    - Set-Cookie
    - HttpOnly
    - SameSite
monitoring:
  applies_to:
  - component
  - flow
  health_signals:
  - name: session_auth.lookup.error.rate
    description: Failures loading or persisting authenticated session state.
  - name: session_auth.expired.rate
    description: Requests rejected because the session expired or was destroyed.
  business_metrics: []
  gaps:
  - Missing session-store and expiry visibility hides auth state drift and logout
    bugs.
family: design-patterns
---

# Explanation

## Recognition

How to identify this pattern in code.

### Signatures

- Server-side session store (Redis, database table, in-memory map)
- `session_id` cookie set on login response
- `Set-Cookie` header with `HttpOnly`, `Secure`, and `SameSite` attributes
- Session middleware (`express-session`, `django.contrib.sessions`, `gorilla/sessions`)
- `req.session` or `request.session` access in request handlers
- Server-side session lookup on every authenticated request
- CSRF tokens paired with sessions (`csrf_token`, `X-CSRF-Token` header)
- Session expiry and idle timeout configuration
- Libraries: `express-session`, `connect-redis`, `django.contrib.sessions`, `flask-session`, `gorilla/sessions`

### Confidence

- **high** -- Session store configured (Redis/DB), `Set-Cookie` with `HttpOnly`/`Secure`/`SameSite`, session middleware registered, and CSRF protection enabled
- **medium** -- `req.session` or `request.session` used in handlers with cookie-based auth, but session store backend unclear
- **low** -- Cookie-based authentication present but no explicit session store or middleware visible (could be signed cookies without server-side state)

## Architecture

Look for server-side session state management with secure cookie transport and CSRF protection.

### Relationship To Other Concepts

- `session-auth` is server-owned auth state carried via cookies or session IDs.
- Prefer `token-auth` when requests authenticate with self-contained bearer tokens.
- Prefer `oauth-oidc` when delegated identity-provider flows are part of the design.

### Review Checklist

- Session IDs are cryptographically random and sufficiently long (128+ bits of entropy)
- Session store has TTL/expiry configured (not unbounded growth)
- Cookies set `HttpOnly`, `Secure`, and `SameSite=Strict` or `SameSite=Lax`
- CSRF protection is enabled for all state-changing requests
- Session is regenerated on login to prevent session fixation
- Logout destroys the server-side session, not just the cookie

### Anti-patterns

- Storing sensitive data (passwords, tokens) directly in the session object
- Using in-memory session store in production (lost on restart, no horizontal scaling)
- Missing `HttpOnly`/`Secure` flags on session cookies (vulnerable to XSS and MITM)
- No session regeneration on privilege change (session fixation vulnerability)

### Boundary

Use `session-auth` when the important observation is this specific architectural concern within a backend service, storage, or server-side architectural concern.

Do not use it just because a few signatures match; the surrounding responsibilities and architectural role should line up too.
