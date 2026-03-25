# KORD

Auto-generated from frontmatter. Do not edit manually.

## Agents

- `agents/deployer/IDENTITY.md` — Infrastructure operations — deployments, cluster management, kubectl authority
- `agents/designer/IDENTITY.md` — Architecture review and pattern authority — reviews design consistency and identifies patterns
- `agents/sauron/IDENTITY.md` — Monitoring, observability, and code validation — ensures projects are observable and correct
- `agents/scribe/IDENTITY.md` — Documentation gate and runtime linker — sole authority for writing to kordinate and memory paths

## Memory

- `agents/deployer/memory/infra.md` — Infrastructure Reference
- `agents/deployer/memory/migration.md` — Full migration lifecycle for deployments
- `agents/deployer/memory/tools.md` — Deployer tools reference — postgres.py and local utilities
- `agents/deployer/memory/troubleshooting.md` — Common deployment issues and their fixes
- `agents/designer/memory/app-contract.md` — App Contract
- `agents/designer/memory/libraries.md` — Index of shared libraries that implement patterns across projects
- `agents/designer/memory/libraries/klog.md` — klog library reference
- `agents/designer/memory/libraries/nokrashi-tools.md` — nokrashi-tools library reference
- `agents/designer/memory/libraries/orchestrator.md` — orchestrator library reference
- `agents/designer/memory/libraries/stoik.md` — stoik library reference
- `agents/designer/memory/patterns.md` — Index of recognized architectural patterns by category
- `agents/designer/memory/patterns/api-gateway.md` — Api Gateway architectural pattern
- `agents/designer/memory/patterns/backpressure.md` — Backpressure architectural pattern
- `agents/designer/memory/patterns/bulkhead.md` — Bulkhead architectural pattern
- `agents/designer/memory/patterns/choreography.md` — Choreography architectural pattern
- `agents/designer/memory/patterns/circuit-breaker.md` — Circuit Breaker architectural pattern
- `agents/designer/memory/patterns/cqrs.md` — Cqrs architectural pattern
- `agents/designer/memory/patterns/ddd.md` — Ddd architectural pattern
- `agents/designer/memory/patterns/etl.md` — Etl architectural pattern
- `agents/designer/memory/patterns/event-sourcing.md` — Event Sourcing architectural pattern
- `agents/designer/memory/patterns/hexagonal.md` — Hexagonal architectural pattern
- `agents/designer/memory/patterns/plugin.md` — Plugin architectural pattern
- `agents/designer/memory/patterns/retry.md` — Retry architectural pattern
- `agents/designer/memory/patterns/saga.md` — Saga architectural pattern
- `agents/designer/memory/patterns/service-manager.md` — Service Manager architectural pattern
- `agents/designer/memory/patterns/sidecar.md` — Sidecar architectural pattern
- `agents/designer/memory/patterns/stream-to-store.md` — Stream To Store architectural pattern
- `agents/designer/memory/tools.md` — Designer tools reference — Gemini MCP for architecture validation
- `agents/designer/memory/workflow.md` — Designer review workflow — identify, compare, review, report
- `agents/sauron/memory/grafana_renderer.md` — Prioritize Grafana renderer for visual dashboard auditing over JSON-only analysis
- `agents/sauron/memory/logging.md` — Structured logging standards across all projects
- `agents/sauron/memory/monitoring.md` — Four-layer monitoring model — physical, application, business, alerting
- `agents/sauron/memory/tools.md` — Sauron tools reference — klog, nokrashi-tools, Grafana MCP
- `agents/sauron/memory/workflow.md` — Sauron workflow — understand, implement, validate, report
- `agents/scribe/memory/templates/agents/sauron/metrics.md` — <Project> — Metrics
- `agents/scribe/memory/templates/agents/sauron/vitals.md` — Template for project vitals documentation
- `agents/scribe/memory/tools.md` — Scribe tools reference — Gemini MCP for doc review
- `agents/scribe/memory/workflow.md` — Scribe authentication and write workflow

## Kords

- `kords/create-kord/contract.md` — Define a new kord between agents
- `kords/deployer-default/contract.md` — General deployment and cluster questions
- `kords/designer-default/contract.md` — General architecture and design questions
- `kords/monitoring-impact/contract.md` — Monitoring impact assessment for infrastructure changes
- `kords/onboard/contract.md` — Onboard a new agent or sync existing agents to the runtime
- `kords/pattern-review/contract.md` — Architecture review for deployment and monitoring changes
- `kords/remember/contract.md` — Write a memory for an agent — handles scope, paths, and registry updates
- `kords/sauron-default/contract.md` — General monitoring and observability questions
- `kords/scribe-default/contract.md` — General documentation and template questions
