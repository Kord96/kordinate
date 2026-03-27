---
name: kord
description: Send a request to another agent through a kord contract.
curated: true
scope: global
---

Thin wrapper that routes kord requests. Stateless kords run locally, stateful kords go through Beorn.

**Input**: $ARGUMENTS — `<provider> [kord-name] <message>` or `<kord-name> <message>`

## Usage

```
/kord deployer what's running in prod?
/kord scribe remember DNS uses .local domains
/kord designer pattern-review review the deployment changes
/kord remember team coding standards updated
```

## Resolution

1. If first param matches a kord name under `$KORDINATE_HOME/kords/` → use it. Provider from contract.
2. If first param matches an agent name → check if second param is a kord name. If yes, use that kord. If no, use `<agent>-default`.
3. Read `contract.md` frontmatter to get `provider`, `mode`, `skill`.

## Execution

### Stateless (`mode: stateless`)

Handle locally — no Beorn, no agent spawn:

1. Authenticate as provider: `cp $KORDINATE_HOME/profile/locks/<provider> /tmp/.<provider>-auth`
2. Invoke the skill specified in the contract's `skill:` field (e.g., `/remember`, `/sanitize`)
3. Remove auth: `rm /tmp/.<provider>-auth`
4. Return the result.

### Stateful (`mode: stateful`)

Delegate to Beorn's `kord` tool:

1. Call Beorn MCP tool `kord` with `kord_name` and `message`.
2. Beorn handles: contract lookup, expiry/cache check, agent spawning, result caching.
3. If Beorn returns `[cached]` prefix, the result came from cache.
4. Return the result.

Beorn is the sole agent host for stateful kords. It creates a git worktree per agent spawn in `$KORDINATE_HOME`, so memory writes are isolated per agent and merged back into main on completion.

**Connection**: on-cluster via cluster DNS (`beorn.kordinate.svc.cluster.local`), off-cluster via Tailscale.

**No fallback**: if Beorn is unreachable, report the error to the caller. Do NOT fall back to native subagent spawning — stateful kords require Beorn's lifecycle management (worktree creation, memory isolation, merge on completion).
