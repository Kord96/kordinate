---
description: Session-Based Authentication architectural pattern
type: pattern
testable: true
observable: true
curated: true
scope: global
preloaded: none
graphable: true
abstraction: [security]
---
# Session-Based Authentication

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
- Java: `HttpSession` interface, `request.getSession()`, `@SessionScoped`
- Java: Quarkus/Jakarta session cookie handling, Undertow `SessionManager`, `SessionConfig`
- Java: Spring Security form login with session-based authentication (`HttpSecurity.formLogin()`)

### Confidence

- **high** -- Session store configured (Redis/DB), `Set-Cookie` with `HttpOnly`/`Secure`/`SameSite`, session middleware registered, and CSRF protection enabled
- **medium** -- `req.session` or `request.session` used in handlers with cookie-based auth, but session store backend unclear
- **low** -- Cookie-based authentication present but no explicit session store or middleware visible (could be signed cookies without server-side state)

## Architecture

Look for server-side session state management with secure cookie transport and CSRF protection.

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
