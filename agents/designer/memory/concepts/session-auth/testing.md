---
description: Session-Based Authentication — testing guidance
type: supplementary
curated: true
scope: global
preloaded: none
---
# Testing

- Test session creation on login and destruction on logout (server-side deletion, not just cookie removal)
- Verify session regeneration on login to prevent session fixation attacks
- Test cookie attributes: assert `HttpOnly`, `Secure`, and `SameSite` flags are set correctly
- Test session expiry by advancing time past the TTL and verifying the session is rejected
- Verify CSRF protection by submitting state-changing requests without the CSRF token and expecting rejection
- Test concurrent sessions: verify behavior when the same user logs in from multiple clients
- Test session store failover — verify graceful degradation when the session backend is unavailable
- Assert that sensitive data (passwords, tokens) is never stored in the session object
