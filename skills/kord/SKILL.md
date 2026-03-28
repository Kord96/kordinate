---
name: kord
description: Send a request to another agent through a kord contract.
curated: true
scope: global
---

> **DEPRECATED**: This skill is being replaced by beorn capability tools. Use capability tools (e.g., write_memory, analyze_architecture) directly.

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

Wrap the caller's message with the lifecycle checklist from [lifecycle-wrapper.md](lifecycle-wrapper.md), then spawn the agent.

**Spawn strategy** — try Beorn first, fall back to local:

1. **Beorn available** (on-cluster or via Tailscale):
   - Call Beorn MCP tool `kord` with `kord_name` and the wrapped message.
   - Beorn handles: expiry/cache check, worktree creation, agent spawning, memory isolation, merge on completion.
   - If Beorn returns `[cached]` prefix, the result came from cache (lifecycle wrapper was not applied).

2. **Beorn unreachable** (offline, no Tailscale, local dev):
   - Spawn via Agent tool with `subagent_type` set to the provider agent name.
   - Pass the wrapped message as the `prompt`.
   - Memory writes go directly to `$KORDINATE_HOME` (no worktree isolation).

**Connection**: on-cluster via cluster DNS (`beorn.kordinate.svc.cluster.local`), off-cluster via Tailscale.

Return the result.
