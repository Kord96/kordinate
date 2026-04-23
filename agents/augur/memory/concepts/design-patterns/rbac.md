---
kind: concept
name: rbac
signatures:
  concept: rbac
  positive:
    strong:
    - explicit role-to-permission mapping plus enforcement middleware or guards
    - user or group assignment to named roles
    medium:
    - role checks exist with some centralized authorization helpers
    weak:
    - scattered role-name conditionals with no stable permission model
  negative:
  - UI-only role checks with no server enforcement
  - one hardcoded superadmin role substituted for a real authorization model
  notes:
  - Keep this distinct from token-auth; RBAC is authorization policy, not credential
    transport.
type: pattern
abstraction:
- security
scope: backend
status: primary
review_questions:
  threshold: 5
  entries:
  - id: rbac-role-permission-model
    prompt: Does the authorization model map users or groups to roles and roles to
      permissions?
    weight: 3
    signals:
    - requires_role
    - has_permission
    - RoleBinding
  - id: rbac-enforcement-layer
    prompt: Are role checks enforced at route, API, or service boundaries rather than
      only in the UI?
    weight: 2
    signals:
    - authorize
    - Roles(
    - canActivate
monitoring:
  applies_to:
  - component
  - flow
  health_signals:
  - name: authorization.denied.rate
    description: Requests or actions denied by RBAC enforcement.
  business_metrics: []
  gaps:
  - Missing authorization-denial visibility hides policy drift and rollout errors.
family: design-patterns
---

# Explanation

## Recognition

How to identify this pattern in code.

### Signatures

- Role definitions with associated permissions (`admin`, `editor`, `viewer`)
- Permission checks: `has_role()`, `has_permission()`, `@requires_role`, `authorize()`
- Middleware or decorators enforcing role requirements on routes or actions
- Role-permission mapping tables in database schemas or config files
- K8s RBAC: `Role`, `ClusterRole`, `RoleBinding`, `ClusterRoleBinding` manifests
- User-role assignment logic or admin interfaces for role management

### Confidence

- **high** -- role-permission mapping table, middleware enforcing role checks on endpoints, and role assignment to users/groups
- **medium** -- role-based conditionals in code (`if user.role == "admin"`) but no formal permission model
- **low** -- user types or levels that loosely map to access tiers without explicit role-permission structure

## Architecture

Look for a clean separation between role definitions, permission assignments, and enforcement points.

### Review Checklist

- Roles follow least-privilege principle (no overly broad `superadmin` that bypasses all checks)
- Permission checks happen at the enforcement layer (middleware/guard), not scattered through business logic
- Role hierarchy is explicit if it exists (admin inherits editor permissions by declaration, not by duplicating them)
- Default role for new users is the most restrictive
- Role changes take effect immediately (no stale cached role data)
- K8s RBAC: namespace-scoped Roles preferred over ClusterRoles where possible

### Anti-patterns

- Hardcoding role names in business logic instead of checking permissions
- God role that bypasses all authorization checks
- Checking roles at the UI layer but not enforcing on the API (cosmetic-only access control)
- Role explosion with one role per user instead of composable permission sets

### Relationship To Other Concepts

- Related to [route-guard](/concepts/route-guard) when frontend navigation is restricted based on roles or permissions.
- Related to [oauth-oidc](/concepts/oauth-oidc) because identity and claims often feed role assignment and policy checks.
- Related to [multi-tenant](/concepts/multi-tenant) when role semantics are scoped per tenant or workspace.

### Boundary

Use `rbac` when access decisions are based primarily on assigned roles and the permissions associated with those roles.

Do not use it for any authorization. The key signal is role-based policy rather than arbitrary attribute- or rule-based access.
