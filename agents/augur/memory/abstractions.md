---
description: Index of abstraction levels used to classify concepts — each answers a distinct architectural question
---

# Abstractions

Every concept in the catalog belongs to one or more abstractions. Abstractions describe the lens through which a concept is useful.

| Abstraction | Description | Examples |
|------------|-------------|---------|
| **architectural** | System-level structure — how services, modules, and layers are organized and separated | hexagonal, microservices, CQRS, event-sourcing, modular-monolith |
| **design** | Code-level structure — how classes, functions, and objects are composed within a component | factory, observer, decorator, strategy, composite |
| **data** | Data movement and persistence — how data is ingested, transformed, cached, queried, and stored | stream-to-store, ETL, cache-aside, materialized-view, sharding |
| **integration** | Cross-boundary communication — how independent components or services coordinate | saga, webhook, API gateway, anti-corruption-layer, strangler-fig |
| **messaging** | Message delivery mechanics — how messages are produced, routed, consumed, and acknowledged | pub-sub, message-queue, outbox, dead-letter, competing-consumers |
| **infrastructure** | Runtime resources — physical or virtual things that exist and need provisioning | connection-pooling, service-mesh, LRU cache, service-discovery |
| **resilience** | Failure tolerance — how the system detects, contains, and recovers from failures | circuit-breaker, bulkhead, retry, graceful-degradation, timeout |
| **concurrency** | Parallel execution — how concurrent work is coordinated without corruption or starvation | actor-model, worker-pool, read-write-lock, future-promise |
| **security** | Access and trust — how identity, authorization, and data protection are enforced | oauth-oidc, rbac, mtls, rate-limiting, tenant-isolation |
| **api** | Interface contracts — how services expose operations and data to consumers | REST, GraphQL, gRPC, BFF, content-negotiation |
| **lifecycle** | Runtime behavior — how a process starts, runs, shuts down, and transitions between states | service-manager, health-check, scheduler, strangler-fig |
| **deployment** | Release mechanics — how software moves from build to production safely and reversibly | blue-green, canary, gitops, immutable-infra, feature-flag |
| **observability** | System visibility — how operators see what the system is doing and detect anomalies | structured-logging, distributed-tracing, metrics-instrumentation |
| **testing** | Verification strategy — how correctness is validated at different boundaries | contract-testing, property-testing, test-doubles, fixture-builder |
| **frontend** | UI composition — how user interfaces are structured, rendered, and state-managed | MVC, MVVM, flux, component, micro-frontend |
| **error-handling** | Failure representation — how errors are modeled, propagated, and handled in code | result-type, monad, null-object |
| **realtime** | Time-sensitive execution — how simulations and real-time systems manage deterministic updates | game-loop, ECS, tick-simulation, spatial-partitioning |
| **ml** | Model lifecycle — how models are trained, versioned, experimented with, and served | feature-store, model-registry, training-pipeline, experiment-framework |
| **compiler** | Language tooling — how source code is parsed, represented, and transformed | lexer-parser, AST, intermediate-representation |
