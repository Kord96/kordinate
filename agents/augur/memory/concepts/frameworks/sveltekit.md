---
kind: framework
name: sveltekit
signatures:
  framework: sveltekit
  manifest_packages:
    package_json:
    - '@sveltejs/kit'
    - sveltekit
  source_extensions:
  - .js
  - .ts
  path_patterns:
    strong:
    - (^|/)src/routes/
    medium:
    - \+server\.(ts|js|mjs|cjs)$
    weak: []
  source_patterns:
    strong:
    - export\s+(async\s+)?function\s+(GET|POST|PUT|DELETE|PATCH)\b
    medium: []
    weak: []
  negative_path_patterns:
  - (^|/)(app|pages)/api/
  negative_source_patterns: []
language: typescript
framework_kind: full-stack
scope: frontend
status: primary
family: frameworks
relationships:
  uses:
  - server-route-registration
traits:
  ui_surface: true
  file_routing_native: true
  server_rendering_native: true
common_failure_modes:
- blurred-client-server-boundaries
- endpoint-and-page-coupling
- load-function-sprawl
---

# Explanation

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
