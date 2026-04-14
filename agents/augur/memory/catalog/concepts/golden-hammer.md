---
description: Golden Hammer anti-pattern
type: anti-pattern
graphable: false
---
# Golden Hammer

## Recognition

How to identify this anti-pattern in code.

### Signatures

- One framework or library used for everything (e.g., Celery for async tasks, cron scheduling, messaging, and orchestration simultaneously)
- Same database serving OLTP, OLAP, caching, and queuing workloads
- A single programming language used across all tiers regardless of fit (frontend, backend, CLI tooling, data pipelines, infrastructure)
- Every problem solved with the same pattern (e.g., everything is a microservice, everything is a stored procedure, everything is a queue)
- Extensive workarounds to force a tool beyond its intended use case

### Confidence

- **high** -- a single technology serves 3+ fundamentally different purposes with documented workarounds for its limitations in each
- **medium** -- architectural decisions consistently favor one tool despite documented better alternatives for specific use cases
- **low** -- team discussions default to "just use X" without evaluating alternatives

## Impact

Forces inappropriate solutions on problems, leading to poor performance, reliability issues, and excessive workaround code.

### Symptoms

- Performance problems in one workload (e.g., analytics queries) degrade another (e.g., transactional writes) because they share infrastructure
- Workaround code exceeds the actual business logic it supports
- The team cannot hire specialists because the tech stack is idiosyncratic
- Upgrading the single tool becomes high-risk because everything depends on it
- New requirements are rejected or awkwardly shoehorned because the chosen tool does not support them natively

### Remediation

- Evaluate each major capability against purpose-built alternatives using a lightweight ADR (Architecture Decision Record)
- Introduce polyglot persistence: use the right data store for each workload (RDBMS for transactions, cache for hot data, warehouse for analytics)
- Decouple workloads so they can migrate to better-fit tools independently
- Establish a technology radar that the team reviews quarterly to stay aware of appropriate tools
- Start with the highest-pain workload: migrate it first as a proof of concept
