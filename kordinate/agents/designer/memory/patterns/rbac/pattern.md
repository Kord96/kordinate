---
description: Role-Based Access Control architectural pattern
type: pattern
testable: true
curated: true
scope: global
preloaded: none
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
