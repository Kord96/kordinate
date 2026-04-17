---
description: Role-Based Access Control architectural pattern
type: pattern
testable: true
graphable: true
abstraction:
- security
status: primary
scope: backend
relationships:
  related_to:
  - route-guard
  - oauth-oidc
  - multi-tenant
aliases: []
disambiguates_from: []
preferred_over: []
implies: []
anti_signals: []
detector_coverage: rich
examples: []
---
# Role-Based Access Control

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
