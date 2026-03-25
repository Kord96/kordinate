# Kords

Inter-agent contracts that define how agents consult each other. Each kord specifies a provider, who can request it, and the response format.

## All Kords

| Kord | Provider | Mode | Requesters | Description |
|------|----------|------|-----------|-------------|
| [deployer-default](deployer-default/contract.md) | deployer | stateful | any | General deployment and cluster questions |
| [designer-default](designer-default/contract.md) | designer | stateful | any | General architecture and design questions |
| [pattern-review](pattern-review/contract.md) | designer | stateful | deployer, sauron | Architecture review for deployment/monitoring changes |
| [sauron-default](sauron-default/contract.md) | sauron | stateful | any | General monitoring and observability questions |
| [monitoring-impact](monitoring-impact/contract.md) | sauron | stateful | deployer | Monitoring impact assessment for infra changes |
| [scribe-default](scribe-default/contract.md) | scribe | stateful | any | General documentation and template questions |
| [create-kord](create-kord/contract.md) | scribe | stateful | any | Define a new kord between agents |
| [onboard](onboard/contract.md) | scribe | stateful | any | Onboard a new agent to the team |
| [remember](remember/contract.md) | scribe | stateless | any | Write a memory for an agent |
| [sanitize](sanitize/contract.md) | scribe | stateless | any | Classify content as config, credential, or memory |

## Modes

- **stateful** — Requires agent context. Routed to Beorn MCP, response is cached until provider state changes.
- **stateless** — Self-contained skill invocation. Runs locally without Beorn.

## Contract Structure

Each kord directory contains:

```
<kord>/
├── contract.md   # Frontmatter (provider, requester, mode) + response format
├── data.md       # Cached response (populated on first consult, stateful only)
└── expiry.sh     # Freshness check (stateful only)
```
