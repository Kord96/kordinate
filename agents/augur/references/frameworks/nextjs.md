---
kind: framework
name: nextjs
signatures:
  framework: nextjs
  manifest_packages:
    package_json:
    - next
  source_extensions:
  - .js
  - .jsx
  - .ts
  - .tsx
  path_patterns:
    strong:
    - (^|/)(app|pages)/api/
    medium: []
    weak: []
  source_patterns:
    strong:
    - export\s+(async\s+)?function\s+(GET|POST|PUT|DELETE|PATCH)\b
    - export\s+\{\s*(GET|POST|PUT|DELETE|PATCH)\s*\}
    medium: []
    weak: []
  negative_path_patterns: []
  negative_source_patterns: []
source:
  memory_framework: memory/catalog/frameworks/nextjs/framework.md
  semantics: memory/catalog/frameworks/nextjs/semantics.yaml
language: typescript
framework_kind: full-stack
scope: frontend
status: primary
---

# Explanation

Next.js is a React-based full-stack framework with file-based routing, server rendering, and API route surfaces.

## Recognition
Common signals:
- `next` dependency
- `app/` or `pages/` routing layout
- `app/api/.../route.ts` or `pages/api/...`
- exported HTTP method functions like `GET` or `POST`

## Architectural implications
- frontend and backend concerns often live in one repo and sometimes one route tree
- file-system routing shapes the component and API topology
- data-fetching choices strongly influence whether boundaries stay clean

## Common failure modes
- server and client responsibilities blur together
- route handlers accumulate backend orchestration without clear service seams
- multiple data-fetching conventions fragment architecture understanding
