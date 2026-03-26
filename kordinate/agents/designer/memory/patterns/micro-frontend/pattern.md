---
description: Micro-Frontend architectural pattern
curated: true
scope: global
preloaded: none
---
# Micro-Frontend

## Recognition

How to identify this pattern in code.

### Signatures

- Independently deployable frontend modules owned by separate teams
- Module federation config (`ModuleFederationPlugin`), import maps, or SystemJS loader
- Shell/host application loading remote micro-apps at runtime
- Iframe isolation, Web Components, or shadow DOM boundaries between modules
- Tools: Webpack Module Federation, single-spa, Bit, Piral, import maps

### Confidence

- **high** -- Webpack Module Federation config or single-spa route registration loading separately deployed frontends
- **medium** -- Independent frontend apps composed at build time or via iframe embedding with a shared shell
- **low** -- Any frontend split across separately maintained packages with some form of runtime composition

## Architecture

Look for independently built and deployed frontend modules composed into a unified application by a shell.

### Review Checklist

- Shared dependencies (React, Angular) are loaded once, not duplicated per micro-frontend
- Module boundaries are enforced -- no direct imports between micro-frontends
- Routing is coordinated by the shell, not duplicated across modules
- Styling is scoped per module (CSS modules, shadow DOM, or naming conventions) to prevent leaks
- Failure in one micro-frontend does not crash the entire application (error boundaries)
- Shared state between modules is minimal and uses a defined contract (events, shared store)

### Anti-patterns

- Micro-frontends sharing a database or global state store (coupling through the back door)
- Duplicating large framework bundles in every micro-frontend
- Tight deployment coupling -- all micro-frontends must deploy together
- No contract or versioning for shared APIs between modules
