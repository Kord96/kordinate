---
description: Lightweight Python web framework with explicit route decorators and extension-based composition
---
# Flask

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
