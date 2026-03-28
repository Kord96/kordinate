## Testing

Verify permission enforcement at every access point, role hierarchy correctness, and least-privilege defaults.

### Unit Tests

- For each role, verify access to permitted endpoints succeeds and access to forbidden endpoints returns 403
- Test role hierarchy: admin inherits editor permissions, editor inherits viewer permissions
- Verify the default role for new users is the most restrictive (viewer or equivalent)
- Test permission changes take effect immediately (no stale role cache serving outdated access)

### Authorization Tests

- Attempt to access a protected resource with no authentication and verify 401
- Attempt to access a resource with valid authentication but insufficient role and verify 403
- Test role escalation: verify a user cannot assign themselves a higher role without proper authorization
- Verify Kubernetes RBAC: namespace-scoped Roles restrict access to only the intended namespace

### Integration Tests

- Assign a role via the admin API, then verify the user can immediately access the newly permitted endpoints
- Revoke a role and verify the user is immediately denied access on the next request
- Test that API-level enforcement matches UI-level enforcement (no cosmetic-only access control)

