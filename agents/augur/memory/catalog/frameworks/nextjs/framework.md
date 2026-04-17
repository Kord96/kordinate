---
description: React-based full-stack framework with file-based routing, server rendering, and API route surfaces
---
# Next.js

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
