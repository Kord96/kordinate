---
kind: framework
name: flask
signatures:
  framework: flask
  manifest_packages:
    pyproject:
    - flask
    requirements:
    - flask
  source_extensions:
  - .py
  path_patterns:
    strong: []
    medium: []
    weak: []
  source_patterns:
    strong:
    - from\s+flask\s+import
    - import\s+flask
    - \bFlask\s*\(
    medium:
    - '@\w+\.route\s*\('
    weak: []
  negative_path_patterns: []
  negative_source_patterns:
  - from\s+fastapi\s+import
  - from\s+django\.urls\s+import
language: python
framework_kind: api-server
scope: backend
status: primary
family: frameworks
relationships:
  implements:
  - rest
  uses:
  - server-route-registration
  related_to:
  - layered
traits:
  api_surface: true
  async_native: false
  validation_native: false
  dependency_injection_native: false
common_failure_modes:
- business-logic-in-routes
- extension-coupling
- implicit-global-state
---

# Explanation

Flask is a lightweight Python web framework centered on explicit route decorators, request handlers, and extension-based composition.

## Recognition
Common signals:
- `from flask import Flask`
- `app = Flask(__name__)`
- `@app.route(...)` or blueprint route decorators
- extensions for auth, ORM, or admin surfaces

## Architectural implications
- route registration is explicit and usually easy to trace
- framework structure is minimal, so architecture discipline comes from the app rather than the framework
- dependency wiring is often implicit through globals, app factories, or extension state

## Common failure modes
- business logic accumulates in route handlers
- application globals make testing and lifecycle management harder
- extension state hides boundaries and dependency ownership
