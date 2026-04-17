---
description: Svelte full-stack framework with file-based routing and colocated server endpoints
---
# SvelteKit

SvelteKit is a Svelte full-stack framework with file-based routing and colocated server endpoints.

## Recognition
Common signals:
- `@sveltejs/kit` dependency
- `src/routes/...`
- `+page.svelte`, `+layout.svelte`, and `+server.ts`
- exported HTTP method functions in route modules

## Architectural implications
- routing, page loading, and server endpoints are tightly tied to the file tree
- frontend and backend seams often depend on route-module discipline
- data loading patterns materially shape boundary clarity

## Common failure modes
- page components and server endpoints become tightly coupled
- `load` functions spread orchestration across many route modules
- backend logic hides inside route files instead of explicit services
