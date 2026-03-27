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

1. If first param matches a kord name under any `$KORDINATE_HOME/agents/*/kords/` directory → use it. Derive provider from the path (`agents/<provider>/kords/<name>/`).
2. If first param matches an agent name → check if second param is a kord name. If yes, use that kord. If no, use `<agent>-default`.
3. Derive `provider` from the path (`agents/<provider>/kords/<name>/`). Read `contract.md` frontmatter for `mode` and `skill`.

## Requester Enforcement

After resolving the kord, check the `requester` field in the contract frontmatter:

- If `requester: any` → proceed.
- If `requester: <agent-name>` or `requester: <agent1>, <agent2>` → check that the calling agent matches one of the listed names. The calling agent is determined by which auth lock exists (`/tmp/.<name>-auth`) or, if no lock exists, the caller is `main`.
- If the caller is not authorized: **refuse the request** and report: "Kord `<name>` is restricted to `<requester>`. Use `/kord <provider>` to consult directly instead."

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
2. Beorn runs a two-stage expiry check via `lib/kord-expiry.sh`, which reads `cache_inputs` from contract.md frontmatter and computes staleness from change magnitude + age decay:
   - **Fresh** (exit 0) — change score below threshold, serve cached `data.md` immediately.
   - **Stale** (exit 1) — no cached data, max age exceeded, or change score above stale_threshold. Spawn the provider agent, regenerate `data.md`.
   - **Uncertain** (exit 2) — change score between thresholds. Beorn reads `review.md`, fills in `{{DIFF}}` (files changed since last snapshot) and `{{CACHED_DATA}}` (current data.md), then spawns a lightweight agent review. If the review responds `VALID`, Beorn updates the snapshot and serves the cache. If `STALE`, Beorn proceeds to full regeneration.
3. After Beorn stores `data.md`, it also runs `cache_snapshot` to store a `.snapshot` file (line counts + md5 hashes of all input files). This powers the magnitude-based expiry on next check.
4. If Beorn returns `[cached]` prefix, the result came from cache. `[cached:revalidated]` means it passed stage 2 review.
5. Return the result.

If Beorn is not available (no MCP connection), fall back to native subagent spawning via the Agent tool — read the contract guidelines and spawn the provider agent directly. No caching in this case.
