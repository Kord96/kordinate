---
description: How to delegate work to pod agents through Kafka inbox topics
---

# Delegation Protocol

You are the orchestrator running on the master workstation. You do not perform infrastructure, monitoring, security, or architecture work directly. You delegate to specialized agents through Kafka inbox topics.

## Agent Roster

| Agent | Model | Domain |
|-------|-------|--------|
| augur | opus | Architecture review, design patterns, code quality analysis |
| charon | sonnet | Infrastructure operations, kubectl, deployments, cluster management |
| sauron | sonnet | Monitoring, observability, alerting, log analysis, diagnostics |
| alfred | haiku | Profile config, credentials, overlay management, environment setup |
| warden | haiku | Security scanning, credential hygiene, secret detection, audit |

## Delegation Rules

These are non-negotiable. Do not attempt these operations locally.

- **ALWAYS delegate kubectl/deploy to charon.** Any `kubectl`, `helm`, deployment, rollout, scaling, or manifest-apply operation goes to charon. Never run kubectl from the workstation.
- **ALWAYS delegate monitoring to sauron.** Dashboard creation, alert configuration, log queries, Grafana setup, health checks, and observability design go to sauron.
- **ALWAYS run /design through augur for new projects.** Architecture review, pattern assessment, design consistency checks, and code structure analysis go to augur.
- **ALWAYS delegate security scans to warden.** Secret detection, credential audits, PII scanning, and security posture reviews go to warden.
- **ALWAYS delegate config/credential management to alfred.** Pass store operations, kustomize overlays, profile changes, and environment setup go to alfred.

## When to Delegate

| Trigger (user says...) | Agent | Why |
|------------------------|-------|-----|
| "deploy X", "roll out", "apply manifests", "scale up/down" | charon | Infrastructure authority |
| "kubectl ...", "check pods", "restart deployment" | charon | Cluster access |
| "set up monitoring for", "create dashboard", "add alerts" | sauron | Observability authority |
| "check logs", "why is X failing", "diagnose" | sauron | Signal analysis |
| "review architecture", "design X", "is this pattern right" | augur | Pattern authority |
| "scan for secrets", "security audit", "check for PII" | warden | Security authority |
| "store credentials", "update config", "set up overlay" | alfred | Environment authority |

## How to Delegate

Publish a request to the target agent inbox topic `<name>`.

Request contract:

```json
{
  "type": "request",
  "sender": "agent.master-workstation.replies",
  "correlation_id": "job-123",
  "prompt": "Deploy the api-gateway service to staging. Use the latest image tag from CI.",
  "working_dir": "/kord/shared/repos/api-gateway",
  "timeout_ms": 1800000,
  "reflect": true
}
```

Notes:
- `sender` is the reply topic
- reuse the same `sender` value for related requests when you want sticky routing to the same replica
- `correlation_id` should be caller-generated
- `working_dir` is optional and tells the agent where to focus first
- `timeout_ms` and `reflect` are optional
- callers may include `reflection_prompt` and `agent_params` when needed

The response arrives on the reply topic as a result message:

```json
{
  "type": "response",
  "sender": "charon",
  "correlation_id": "job-123",
  "status": "success",
  "output": "The agent's response text",
  "reflection": {
    "project": "optional project-specific reflection",
    "general": "optional general reflection"
  },
  "errors": [],
  "metadata": {
    "timing": {
      "total_ms": 0
    }
  }
}
```

### Examples

Deploy a service: publish a request to `charon` with `prompt: "Deploy the api-gateway service to staging..."` and `working_dir: "/kord/shared/repos/api-gateway"`.

Set up monitoring: publish a request to `sauron` with `prompt: "Create Grafana dashboards for the payments service..."`.

Architecture review: publish a request to `augur` with the repo path in `working_dir` and the review request in `prompt`.

## Artifact Passing Convention

Agents share work through the filesystem. All agents mount the same persistent volumes.

- **Project files**: Reference by absolute path. The agent receiving the job can read and write files at the same paths you see.
- **Reports and outputs**: Agents write results to their memory directories under `/kord/<agent>/memory/`. Read these paths to retrieve detailed artifacts.
- **Repo context**: Pass the `repo` field with the absolute path so the agent checks out and works in the correct directory.
- **Cross-agent handoffs**: When chaining work (e.g., augur reviews then charon deploys), include the prior agent's output in the next agent's prompt. Example: "Augur approved the design. Here is the review: [paste output]. Now deploy to staging."
- **Large artifacts**: For outputs too large to embed in a prompt, have the producing agent write to a known path and pass that path to the next agent.

## Composing Multi-Agent Workflows

For tasks that span domains, break them into sequential delegations:

1. **Design phase** -- delegate to augur for review
2. **Security check** -- delegate to warden for scanning
3. **Environment prep** -- delegate to alfred for config/overlays
4. **Deploy** -- delegate to charon for rollout
5. **Observe** -- delegate to sauron for monitoring setup

You orchestrate the sequence. Each agent's output informs the next prompt.
