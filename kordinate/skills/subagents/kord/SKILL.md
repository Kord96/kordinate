---
name: kord
description: Send a request to another agent through a kord contract.
curated: true
scope: global
---

Send a request to another agent through a kord contract.

**Input**: $ARGUMENTS — `[provider] <kord-name> <message>` or `<provider> <message>`

## Usage

```
/kord deployer what's running in prod?
/kord scribe remember DNS uses .local domains
/kord scribe create-kord health checks for sauron
/kord scribe onboard validator for schema validation
/kord designer pattern-review review the deployment changes
/kord remember team coding standards updated
/kord pattern-review review the deployment changes
```

## Resolution

1. If first param matches a kord name under `$KORDINATE_HOME/kords/` → use it. Provider from contract.
2. If first param matches an agent name → check if second param is a kord name. If yes, use that kord. If no, use `<agent>-default`.
3. Read `contract.md` to get provider, mode, skill, and guidelines.

## Execution

1. **Check mode**:
    - `mode: stateless` → invoke the specified skill directly. No agent spawn. Skip to step 4.
    - `mode: stateful` → proceed to freshness check.

2. **Freshness check** (stateful only):
    - Run `$KORDINATE_HOME/kords/<kord>/expiry.sh` if it exists.
    - Exit 0 = fresh. Return cached `data.md` if prompt matches.
    - Exit 1 = stale. Proceed to delegation.

3. **Spawn provider**:
    - Build prompt from contract guidelines + message.
    - Invoke via Beorn or native subagent.
    - Cache result in `$KORDINATE_HOME/kords/<kord>/data.md`.

4. **Return** the result.
