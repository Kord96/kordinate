---
description: Model-View-Controller architectural pattern
type: pattern
testable: true
curated: true
scope: global
preloaded: none
---
# Model-View-Controller

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
