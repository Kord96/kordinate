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

- **Deployer**: `guard-kubectl.sh` checks for `/tmp/.deployer-auth`. Bootstrap operations also need `/tmp/.bootstrap-auth`.
- **Sauron**: `guard-grafana.sh` checks for `/tmp/.sauron-auth`.
