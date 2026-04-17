---
description: Standard Go HTTP server surface built from net/http handlers and mux wiring
---
# net/http

net/http is the standard Go HTTP server surface built from handlers, mux wiring, and listen/serve entrypoints.

## Recognition
Use the detector package under `detectors/facts/frameworks/net-http/` as the deterministic source of truth for framework evidence.

## Architectural implications
- framework scope: `backend`
- framework kind: `api-server`
- framework-native traits and relationships are defined in `semantics.yaml`

## Common failure modes
- handler-bloat
- ad-hoc-middleware
- implicit-routing-sprawl
