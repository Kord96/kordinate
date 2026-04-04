---
name: authenticate
description: Authenticate before performing guarded operations. Copy the agent's lock file, do work, remove it.
disable-model-invocation: true
curated: true
scope: global
---

Authenticate for guarded operations. Each agent has a lock file at `profile/locks/<agent-name>`.

## Procedure

1. `cp profile/locks/<your-agent-name> /tmp/.<your-agent-name>-auth`
2. Perform all guarded operations for the task
3. `rm /tmp/.<your-agent-name>-auth`

Authenticate once per task, not per operation. Remove the auth token when done — never leave it in place.

## Agent-Specific Notes

- **Charon**: use `/tmp/.charon-auth` for current deployment and kubectl guard flows. Some legacy KORD-based hooks may still refer to `deployer` auth while that compatibility layer exists.
- **Sauron**: current Grafana guard flows use `/tmp/.sauron-auth`.

## Legacy compatibility

Older KORD-based hooks and `/kord` compatibility paths may still reference legacy agent names such as `deployer` and `designer`. Treat those as compatibility behavior only; the canonical agent names are `charon` and `augur`.

For new guard integrations, prefer the canonical current agent names rather than adding more legacy aliases.
