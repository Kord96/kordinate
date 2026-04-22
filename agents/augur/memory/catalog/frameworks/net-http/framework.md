---
description: Standard Go HTTP server surface built from net/http handlers and mux wiring
---
# net/http

net/http is the standard Go HTTP server surface built from handlers, mux wiring, and listen/serve entrypoints.

## Recognition
Use the framework reference in `references/frameworks/` as the canonical shared explanation and signatures source. Deterministic detector policy or rules, when present, live under `detectors/frameworks/net-http/`.

## Architectural implications
- framework scope: `backend`
- framework kind: `api-server`
- framework-native traits and relationships are defined in `semantics.yaml`

## Common failure modes
- handler-bloat
- ad-hoc-middleware
- implicit-routing-sprawl
