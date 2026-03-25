# KORD

Auto-generated from frontmatter. Do not edit manually.

## Agents

- `agents/deployer/IDENTITY.md` — Infrastructure operations — deployments, cluster management, kubectl authority
- `agents/designer/IDENTITY.md` — Architecture review and pattern authority — reviews design consistency and identifies patterns
- `agents/sauron/IDENTITY.md` — Monitoring, observability, and code validation — ensures projects are observable and correct
- `agents/scribe/IDENTITY.md` — Documentation gate and runtime linker — sole authority for writing to kordinate and memory paths

## Memory

- `agents/claude/memory/scratchpad.md` — Operational notes and observations
- `agents/deployer/memory/infra.md` — Infrastructure Reference
- `agents/deployer/memory/migration.md` — Full migration lifecycle for deployments
- `agents/deployer/memory/scratchpad.md` — Deployer working notes and observations
- `agents/deployer/memory/tools.md` — Deployer tools reference — postgres.py and local utilities
- `agents/deployer/memory/troubleshooting.md` — Common deployment issues and their fixes
- `agents/designer/memory/app-contract.md` — App Contract
- `agents/designer/memory/patterns.md` — Index of recognized architectural patterns by category
- `agents/designer/memory/patterns/api-gateway/pattern.md` — Api Gateway architectural pattern
- `agents/designer/memory/patterns/backpressure/pattern.md` — Backpressure architectural pattern
- `agents/designer/memory/patterns/bulkhead/pattern.md` — Bulkhead architectural pattern
- `agents/designer/memory/patterns/choreography/pattern.md` — Choreography architectural pattern
- `agents/designer/memory/patterns/circuit-breaker/pattern.md` — Circuit Breaker architectural pattern
- `agents/designer/memory/patterns/cqrs/pattern.md` — Cqrs architectural pattern
- `agents/designer/memory/patterns/ddd/pattern.md` — Ddd architectural pattern
- `agents/designer/memory/patterns/etl/pattern.md` — Etl architectural pattern
- `agents/designer/memory/patterns/event-sourcing/pattern.md` — Event Sourcing architectural pattern
- `agents/designer/memory/patterns/hexagonal/pattern.md` — Hexagonal architectural pattern
- `agents/designer/memory/patterns/plugin/pattern.md` — Plugin architectural pattern
- `agents/designer/memory/patterns/retry/pattern.md` — Retry architectural pattern
- `agents/designer/memory/patterns/saga/pattern.md` — Saga architectural pattern
- `agents/designer/memory/patterns/service-manager/orchestrator.md` — orchestrator library reference
- `agents/designer/memory/patterns/service-manager/pattern.md` — Service Manager architectural pattern
- `agents/designer/memory/patterns/sidecar/pattern.md` — Sidecar architectural pattern
- `agents/designer/memory/patterns/stream-to-store/pattern.md` — Stream To Store architectural pattern
- `agents/designer/memory/patterns/stream-to-store/stoik.md` — stoik library reference
- `agents/designer/memory/pending/klog.md` — klog library reference
- `agents/designer/memory/pending/nokrashi-tools.md` — nokrashi-tools library reference
- `agents/designer/memory/tools.md` — Designer tools reference — Gemini MCP for architecture validation
- `agents/designer/memory/workflow.md` — Designer review workflow — identify, compare, review, report
- `agents/sauron/memory/grafana_renderer.md` — Prioritize Grafana renderer for visual dashboard auditing over JSON-only analysis
- `agents/sauron/memory/logging.md` — Structured logging standards across all projects
- `agents/sauron/memory/monitoring.md` — Four-layer monitoring model — physical, application, business, alerting
- `agents/sauron/memory/scratchpad.md` — Sauron working notes and observations
- `agents/sauron/memory/tools.md` — Sauron tools reference — klog, nokrashi-tools, Grafana MCP
- `agents/sauron/memory/workflow.md` — Sauron workflow — understand, implement, validate, report
- `agents/scribe/memory/scratchpad.md` — Scribe working notes and observations
- `agents/scribe/memory/skill-marketplace-evaluation.md` — Evaluation of external skill marketplaces (anthropic-agent-skills, alirezarezvani/claude-skills) for integration into deployer, sauron, designer, scribe — verdicts, priorities, cross-agent dependencies
- `agents/scribe/memory/templates/agents/sauron/metrics.md` — <Project> — Metrics
- `agents/scribe/memory/templates/agents/sauron/vitals.md` — Template for project vitals documentation
- `agents/scribe/memory/tools.md` — Scribe tools reference — Gemini MCP for doc review
- `agents/scribe/memory/workflow.md` — Scribe authentication and write workflow

## Kords

- `kords/audit/contract.md` — Read-only health check for memory and kordinate system — scan and report issues
- `kords/create-kord/contract.md` — Define a new kord between agents
- `kords/deployer-default/contract.md` — General deployment and cluster questions
- `kords/designer-default/contract.md` — General architecture and design questions
- `kords/monitoring-impact/contract.md` — Monitoring impact assessment for infrastructure changes
- `kords/onboard/contract.md` — Onboard a new agent to the team
- `kords/pattern-review/contract.md` — Architecture review for deployment and monitoring changes
- `kords/remember/contract.md` — Write a memory for an agent — handles scope, paths, and registry updates
- `kords/sanitize/contract.md` — Classify content as config, credential, or memory — routes to correct destination
- `kords/sauron-default/contract.md` — General monitoring and observability questions
- `kords/scribe-default/contract.md` — General documentation and template questions

## Shared

- `shared/auth-protocol.md` — Instructs agents to authenticate before guarded operations
- `shared/credentials-protocol.md` — All credentials managed through pass store — never hardcoded in manifests or config
- `shared/memory-protocol.md` — Instructs agents to save insights via /kord remember before finishing
