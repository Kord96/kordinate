# kordinate

An agent operations framework for multi-cluster Kubernetes infrastructure.

Kordinate provides specialized agents, safety guardrails, and a GitOps pipeline — orchestrated through an AI coding assistant running inside a Kubernetes pod.

## Quick Start

```bash
git clone <repo-url> ~/kordinate
cd ~/kordinate
./installer/link-claude.sh              # link framework into ~/.claude/
./installer/kordinate-cli init   # bootstrap k8s + workstation
```

## Documentation

**[kord96.github.io/kordinate](https://kord96.github.io/kordinate/)**

| Page | Topic |
|------|-------|
| [Infrastructure](https://kord96.github.io/kordinate/infrastructure/) | Clusters, observability, worktree sessions |
| [Agents](https://kord96.github.io/kordinate/agents/) | Agent roles, commands, safety hooks |
| [Hooks](https://kord96.github.io/kordinate/hooks/) | Safety guardrails and automation |
| [Consultation](https://kord96.github.io/kordinate/consultation/) | Cross-agent queries and caching |
| [Memory](https://kord96.github.io/kordinate/memory/) | Static, dynamic, and project memory |
| [Reference](https://kord96.github.io/kordinate/reference/patterns/) | Design patterns, libraries, link mapping |
