---
kind: concept
name: mvc
signatures: {}
type: pattern
abstraction:
- architectural
- frontend
scope: frontend
status: specialized
family: design-patterns
---

# Explanation

## Recognition

How to identify this pattern in code.

### Signatures

- Separate `models/`, `views/`, `controllers/` directories or class suffixes (`UserController`, `UserModel`)
- Controllers handling HTTP input, delegating to models, selecting views
- Models managing data access and business logic, no rendering or request handling
- Views/templates rendering output from model data, no business logic
- Frameworks: Django (MTV variant), Rails, Spring MVC, ASP.NET MVC, Laravel

### Confidence

- **high** -- Framework-enforced MVC structure with distinct model, view, and controller layers
- **medium** -- Clear separation of data/logic/presentation across files but no formal MVC framework
- **low** -- Some separation of concerns between data handling and rendering, but boundaries are blurred

## Architecture

Look for strict separation between data (model), presentation (view), and input handling (controller).

### Relationship To Other Concepts

- `mvc` is an application coordination pattern, not a statement about deployment style.
- It often appears inside a `layered` application.
- In component-based frontends, MVC may be absent or only partially visible.
- Prefer `component` when the code is primarily organized as a UI component tree rather than controller/view classes.
- Prefer `mvvm` instead when reactive ViewModel state is the dominant coordination mechanism rather than controller-driven request handling.

### Review Checklist

- Controllers are thin -- delegate to models/services, do not contain business logic
- Models have no knowledge of views or HTTP layer
- Views contain only presentation logic -- no database queries or business rules
- Input validation happens at the controller or a dedicated validation layer, not scattered across all three

### Anti-patterns

- Fat controllers containing business logic, database queries, and response formatting
- Views executing database queries or mutating model state
- Models importing view or controller modules (circular dependency)
- Skipping the controller and calling models directly from route definitions

### Boundary

Use `mvc` when the important observation is this specific architectural concern within a frontend, UI, or client-side architectural concern.

Do not promote it above a broader parent concept unless the specialization itself is what materially explains the design.
