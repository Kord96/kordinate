---
description: Minimal Node.js web framework with middleware chaining and explicit route registration
---
# Express

Express is a minimal Node.js web framework built around middleware chains and explicit route registration.

## Recognition
Common signals:
- `require('express')` or `import express`
- `express()`
- `app.get(...)`, `app.post(...)`, or `router.use(...)`
- middleware stacks handling auth, parsing, and error flow

## Architectural implications
- middleware order is a first-class runtime concern
- route boundaries are easy to expose but easy to overload with business logic
- typing and validation quality depend on local conventions and libraries

## Common failure modes
- route handlers swallowing orchestration and business logic
- implicit middleware ordering causing auth or error regressions
- weak request/response typing allowing contract drift
