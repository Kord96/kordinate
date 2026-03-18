# agents/

Agent definitions, commands, and memory. See [../README.md](../README.md) for the agent table, hooks, and commands.

## Lock-Based Authorization

Agents authorize themselves by placing a lock file before operating:

1. Agent copies lock from `profile/locks/<agent>` to `/tmp/.<agent>-auth`
2. Hook compares lock file with `/tmp/` file
3. Agent removes lock file after completing work

## Consultation Protocol

Ask an agent a question without transferring full control:

```
/consult deployer "Is your-app healthy on cluster-a?"
```

| Agent | Expertise |
|-------|-----------|
| designer | Architecture, components, failure modes, data flow, design patterns |
| sauron | Metrics, health checks, log events, dashboards |
| deployer | Cluster state, pod status, deployment status, versions, networking |
