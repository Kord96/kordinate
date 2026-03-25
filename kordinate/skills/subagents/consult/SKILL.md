---
name: consult
description: Consult an agent via kord protocol. Resolves the contract, checks mode (stateless/stateful), handles caching.
curated: true
scope: global
---

Consult an agent through a kord contract.

**Input**: $ARGUMENTS (required: `<agent-or-kord> "<prompt>"`)

## Usage

```
/consult deployer "what's running in prod?"
/consult scribe remember deployer "DNS uses .local domains"
/consult pattern-review "review the deployment changes"
```

## Procedure

1. **Resolve kord**:
    - If target matches a kord directory under `$KORDINATE_HOME/kords/<target>/`, use it.
    - Otherwise, use `<target>-default` as the kord name.
    - Read `contract.md` to get provider, mode, and guidelines.

2. **Check mode**:
    - `mode: stateless` → invoke the specified skill directly. No agent spawn. Skip to step 5.
    - `mode: stateful` → proceed to freshness check and delegation.

3. **Freshness check** (stateful mode only):
    - Run `$KORDINATE_HOME/kords/<kord>/expiry.sh` if it exists.
    - Exit 0 = fresh. Check for cached `data.md` — if the prompt matches, return cached result.
    - Exit 1 = stale. Proceed to delegation.

4. **Delegate**:
    - Build prompt from contract guidelines + user prompt.
    - Invoke provider via Beorn (`mcp__beorn__stateful`) or native subagent spawn.
    - Cache result in `$KORDINATE_HOME/kords/<kord>/data.md`.

5. **Return** the result.
