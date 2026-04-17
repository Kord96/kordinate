---
description: Middleware-oriented Node.js framework emphasizing async composition and explicit context handling
---
# Koa

Koa is a middleware-oriented Node.js framework that emphasizes async composition and explicit request context handling.

## Recognition
Common signals:
- `import Koa` or `require('koa')`
- `new Koa()`
- router registration layered on top of middleware
- `ctx` mutation and async middleware chains

## Architectural implications
- the middleware pipeline is the dominant composition surface
- auth, validation, and response shaping often happen through stacked middleware
- architecture quality depends on keeping `ctx` usage and middleware responsibilities disciplined

## Common failure modes
- middleware order becomes implicit control flow
- request context turns into shared mutable state
- business logic leaks into middleware instead of staying in application services
