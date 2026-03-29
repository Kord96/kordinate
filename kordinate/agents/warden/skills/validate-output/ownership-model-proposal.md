# Ownership-Based File Protection Model

## Status

Proposal -- replaces the `curated` flag in KORD.json with ownership-derived protection.

## Problem

The current guard model has one protection level: `curated: true`. This flag is set on 798 of 821 registered files. In practice, 784 of those are knowledge files (concept catalogs, memory topics, AST rules) that the owning agent should write freely. The remaining 14 are genuine framework files (IDENTITY.md, shared protocols) that should be locked.

The result: agents must authenticate as scribe to edit their own knowledge. This creates unnecessary friction, adds latency to every knowledge write, and overloads scribe's role. Scribe should gate framework changes, not rubber-stamp an agent editing its own concept catalog.

## Design

Three file categories replace the single `curated` boolean.

### 1. Framework files

**What:** IDENTITY.md, SKILL.md, hooks, shared protocols, settings, KORD.json itself.

**Rule:** Only modifiable via `install --local` or register procedures. The guard denies all direct writes. No agent auth bypasses this -- not even scribe.

**Identification in KORD.json:** `"framework": true`

**Current files that qualify (14):**

```
agents/*/IDENTITY.md              (7 files)
shared/auth-protocol.md
shared/credentials-protocol.md
shared/gemini-protocol.md
shared/memory-protocol.md
shared/shared/auth-protocol.md
shared/shared/credentials-protocol.md
shared/shared/memory-protocol.md
```

Plus any future SKILL.md files, hook scripts, and config-acl.yaml if registered.

### 2. Knowledge files

**What:** Concept catalogs, memory topic files, AST rules, kord contracts, routes.yaml. The bulk of the registry (784 files today).

**Rule:** The owning agent writes freely. Other agents must go through kord to request changes from the owner. No authentication required for the owner; denied for everyone else unless they use a kord contract.

**Identification in KORD.json:** No `framework` flag (or `"framework": false`). Ownership derived from path.

**Ownership derivation:**

```
agents/<name>/*  -->  owned by <name>
```

Examples:
- `agents/augur/memory/concepts/adapter/pattern.md` --> owned by `augur`
- `agents/sauron/memory/grafana_renderer.md` --> owned by `sauron`
- `agents/scribe/memory/scratchpad.md` --> owned by `scribe`

Files under `shared/` have no single owner. These should be `framework: true` (shared protocols) or handled by a dedicated rule (shared memory, if any non-framework shared files exist in the future).

### 3. Runtime output

**What:** Scratchpads, atlas.json, stories, journey files -- output that an agent produces during a task.

**Rule:** The owning agent writes freely. Warden validates on demand via completion token (the existing `validate-output` skill). No guard enforcement at write time; enforcement happens at the reporting boundary.

**Identification:** These are the files currently registered with `"curated": false` -- scratchpads and routes.yaml. They keep their current behavior (no guard block). The distinction from knowledge is that runtime output is ephemeral and validated post-hoc rather than guarded pre-write.

In practice, runtime output files do not need a separate KORD.json category. They are simply knowledge files (owned by path) that happen to also be validated by warden. The guard treats them identically to knowledge.

## Guard Logic

### New `guard_write` for `.kord/` paths

Replace the current block (lines 97-119 of guard.sh) with:

```bash
case "$file_path" in
  */.kord/*)
    local kord_json="$KORD_HOME/KORD.json"

    # 1. Check if framework file
    if [ -f "$kord_json" ]; then
      local is_framework
      is_framework=$(jq -r --arg p "$file_path" \
        '.[] | select(.path and ($p | endswith(.path))) | .framework // false' \
        "$kord_json" 2>/dev/null | head -1)
      [ "$is_framework" = "true" ] && \
        deny "Framework file. Modify via install --local in the kordinate repo."
    fi

    # 2. Check ownership for knowledge files
    local path_agent
    path_agent=$(echo "$file_path" | sed -n 's|.*/.kord/agents/\([^/]*\)/.*|\1|p')

    if [ -n "$path_agent" ]; then
      # Path is under agents/<name>/. Check if the current agent is the owner.
      local current_agent
      current_agent=$(get_current_agent)

      if [ "$current_agent" = "$path_agent" ]; then
        allow  # Owner writes freely
      else
        deny "File owned by $path_agent. Use /consult $path_agent to request changes."
      fi
    fi

    # 3. Shared files (not under agents/) that aren't framework -- fallback to scribe
    check_auth scribe && allow
    deny "Shared kordinate file. Requires scribe authentication."
    ;;
esac
```

### The hard part: `get_current_agent`

The guard hook runs as a PreToolUse hook in Claude Code. It receives the tool name and tool input as JSON on stdin. It does NOT receive the identity of the calling agent.

**Four approaches, in order of preference:**

#### Option A: Auth file inference (recommended -- zero new infrastructure)

Every agent that performs guarded operations already runs `/authenticate`, which creates `/tmp/.<agent-name>-auth`. The guard can check which auth files exist:

```bash
get_current_agent() {
  for auth_file in /tmp/.*-auth; do
    [ -f "$auth_file" ] || continue
    local name
    name=$(basename "$auth_file" | sed 's/^\.\(.*\)-auth$/\1/')
    # Verify the lock matches (not stale)
    local lock="$KORD_HOME/profile/locks/$name"
    if [ -f "$lock" ] && [ "$(cat "$auth_file")" = "$(cat "$lock")" ]; then
      echo "$name"
      return
    fi
  done
  echo "main"  # Default: main orchestrator session
}
```

**Trade-offs:**
- Works today with no changes to agent boot or hook registration.
- If no agent is authenticated, defaults to `main`. Main can write to any agent's knowledge (it's the orchestrator). This is correct -- main spawns agents and sometimes writes on their behalf.
- If an agent forgets to authenticate before writing knowledge, it falls through to `main` and is allowed. This is a soft boundary, not a hard one. Acceptable because knowledge writes are lower-stakes than framework writes.
- If two agents are authenticated simultaneously (unusual but possible), this returns the first match. In practice, agents authenticate, do work, then remove auth. Overlap is rare.

**Weakness:** Agents that only write knowledge (not deployer/kubectl or sauron/grafana) don't currently authenticate at all. They would need to start authenticating, OR we accept that unauthenticated writes from main are allowed.

#### Option B: Environment variable set at agent spawn

The `agent-memory.sh` hook already runs at PreToolUse for SubAgent spawns and knows the agent name. It could write an env var or a temp file:

```bash
# In agent-memory.sh, after resolving AGENT:
echo "$AGENT" > /tmp/.kord-current-agent
```

The guard reads `/tmp/.kord-current-agent` to determine who is running.

**Trade-offs:**
- Simple to implement.
- Requires modifying `agent-memory.sh` (adding one line).
- The file persists after the agent exits. Need cleanup, or accept staleness.
- Subagent spawns are the only time we reliably know the agent name in a hook.

#### Option C: Derive from file path context in tool_input

When an agent writes to its own knowledge, the path contains the agent name. The guard already extracts `path_agent`. If the write target is `agents/augur/memory/...`, we know it's augur's territory. The question is whether the *writer* is augur.

We can't confirm the writer's identity from the path alone. But we can adopt a pragmatic rule: **if the path is under `agents/<name>/` and is not framework, allow the write**. The assumption is that agents don't write to each other's knowledge directories unprompted.

```bash
# Simplified: trust the path
if [ -n "$path_agent" ] && [ "$is_framework" != "true" ]; then
  allow  # Any agent can write to non-framework agent paths
fi
```

**Trade-offs:**
- Zero infrastructure. No auth files, no env vars.
- Relies on convention: agents don't cross-write. If agent A writes to agent B's knowledge, the guard won't stop it.
- This is the weakest boundary but may be sufficient. Cross-agent knowledge writes would be a code smell that warden can flag in validation rather than block at write time.

#### Option D: CLAUDE_AGENT_NAME in hook input (requires Claude Code changes)

The ideal solution: Claude Code passes the agent identity in the hook input JSON. Something like:

```json
{
  "tool_name": "Write",
  "tool_input": { "file_path": "..." },
  "agent": { "name": "augur", "type": "subagent" }
}
```

**Trade-offs:**
- Perfect solution. No heuristics, no temp files.
- Requires an upstream change to Claude Code's hook protocol. Not available today.
- Worth filing as a feature request regardless.

### Recommended approach: Option A + Option C fallback

Use auth-file inference when an auth file exists. Fall back to path-trust when no auth is active. This gives strong boundaries for agents that authenticate (deployer, sauron, scribe) and pragmatic boundaries for knowledge-only agents (augur, warden).

```bash
get_current_agent() {
  # Check authenticated agents first
  for auth_file in /tmp/.*-auth; do
    [ -f "$auth_file" ] || continue
    local name
    name=$(basename "$auth_file" | sed 's/^\.\(.*\)-auth$/\1/')
    local lock="$KORD_HOME/profile/locks/$name"
    if [ -f "$lock" ] && [ "$(cat "$auth_file")" = "$(cat "$lock")" ]; then
      echo "$name"
      return
    fi
  done
  echo ""  # Unknown -- caller should use path-trust fallback
}

# In guard_write, after extracting path_agent:
local current_agent
current_agent=$(get_current_agent)

if [ -n "$current_agent" ]; then
  # Strong check: authenticated agent must match path owner
  [ "$current_agent" = "$path_agent" ] && allow
  [ "$current_agent" = "main" ] && allow  # Main orchestrator can write anywhere
  deny "File owned by $path_agent. You are authenticated as $current_agent."
else
  # Weak check: no auth active, trust the path (non-framework only)
  [ -n "$path_agent" ] && allow
fi
```

## KORD.json Migration

### Schema change

Replace `"curated": true/false` with `"framework": true` (present only on framework files). Remove `curated` entirely.

Before:
```json
{"path": "agents/augur/IDENTITY.md", "curated": true, "preloaded": "designer"}
{"path": "agents/augur/memory/concepts/adapter/pattern.md", "curated": true}
{"path": "agents/augur/memory/scratchpad.md"}
```

After:
```json
{"path": "agents/augur/IDENTITY.md", "framework": true, "preloaded": "designer"}
{"path": "agents/augur/memory/concepts/adapter/pattern.md"}
{"path": "agents/augur/memory/scratchpad.md"}
```

### Migration script

```bash
#!/bin/bash
# migrate-kord-json.sh
# Converts curated -> framework for the 14 framework files, drops curated from the rest.

KORD="$KORDINATE_HOME/KORD.json"

# Framework file patterns (paths that get framework: true)
FRAMEWORK_PATTERNS=(
  "IDENTITY.md"
  "shared/auth-protocol.md"
  "shared/credentials-protocol.md"
  "shared/gemini-protocol.md"
  "shared/memory-protocol.md"
  "shared/shared/auth-protocol.md"
  "shared/shared/credentials-protocol.md"
  "shared/shared/memory-protocol.md"
)

# Build jq filter: mark framework files, remove curated from all
jq_filter='[.[] |
  if (.path | test("IDENTITY\\.md$")) then
    del(.curated) | .framework = true
  elif (.path | test("^shared/")) then
    del(.curated) | .framework = true
  else
    del(.curated)
  end
]'

jq "$jq_filter" "$KORD" > "${KORD}.tmp" && mv "${KORD}.tmp" "$KORD"
echo "Migrated $(jq '[.[] | select(.framework == true)] | length' "$KORD") framework files"
echo "Freed $(jq '[.[] | select(.framework != true)] | length' "$KORD") knowledge files from curation"
```

### Guard.sh migration

The guard must handle both schemas during transition:

```bash
# Backward-compatible check: support both curated and framework
local is_framework
is_framework=$(jq -r --arg p "$file_path" \
  '.[] | select(.path and ($p | endswith(.path))) |
   if .framework == true then "true"
   elif .framework != null then "false"
   else .curated // "false"  # Legacy fallback
   end' "$kord_json" 2>/dev/null | head -1)
```

Remove the legacy fallback after all installations have been updated.

## What Changes for Each Agent

| Agent | Before | After |
|-------|--------|-------|
| **augur** | Needs scribe auth to edit any of its 776 concept/memory files | Writes freely to `agents/augur/*` (non-framework) |
| **sauron** | Needs scribe auth for its memory files | Writes freely to `agents/sauron/*` |
| **charon** | Needs scribe auth for its memory files | Writes freely to `agents/charon/*` |
| **warden** | Needs scribe auth for its memory files | Writes freely to `agents/warden/*` |
| **alfred** | Needs scribe auth for its memory files | Writes freely to `agents/alfred/*` |
| **scribe** | Authenticates to write anywhere in .kord/ | Writes freely to `agents/scribe/*`. Still authenticates for shared/ files not marked framework |
| **main** | Goes through scribe for everything | Allowed everywhere as orchestrator (via auth fallback) |

## What Changes for Scribe

Scribe's role narrows from "gate all curated writes" to:

1. **Framework changes**: These are blocked for everyone, including scribe. Framework files change only through `install --local`. Scribe's auth is no longer relevant here.
2. **Shared non-framework files**: If any exist in the future (e.g., shared memory), scribe still gates these.
3. **Cross-agent knowledge requests**: When agent A wants to modify agent B's knowledge, it goes through a kord contract. Scribe may mediate this if needed, but the primary path is direct agent-to-agent via kord.

The `write_memory` MCP tool (beorn) continues to work as-is. It writes to `agents/<name>/memory/`, and the guard will recognize the path owner. If the calling agent is authenticated, ownership is verified. If not, path-trust allows it.

## What Changes for Warden

Warden gains responsibility for framework file integrity:

1. **Validate-output** (existing): Continues to validate runtime output with completion tokens.
2. **Framework audit** (new, optional): Warden can periodically verify that framework files on disk match the installed versions from the kordinate repo. This is a post-hoc check, not a guard-time check.
3. **Cross-write detection** (new, optional): Warden can scan git history for writes where an agent edited another agent's knowledge directory -- a convention violation worth flagging even if the guard allowed it under path-trust.

## Rollout Plan

1. **Phase 1 -- Schema migration**: Add `framework` field to the 14 framework files in KORD.json. Keep `curated` on all files. Guard checks `framework` first, falls back to `curated`. Zero behavior change.

2. **Phase 2 -- Ownership logic**: Add `get_current_agent` and ownership check to `guard_write`. Framework files are hard-blocked. Knowledge files use auth + path-trust. Run for a week; monitor deny logs.

3. **Phase 3 -- Drop curated**: Remove `curated` from all KORD.json entries. Remove legacy fallback from guard. Update `install --local` to use the new schema.

4. **Phase 4 -- File request to Claude Code**: Request `agent.name` in hook input JSON (Option D). When available, replace auth-inference and path-trust with authoritative identity.

## Open Questions

1. **Should main be allowed to write to any agent's knowledge?** The proposal says yes (orchestrator privilege). Alternative: main must also go through kord contracts. This is stricter but adds friction for common operations like "update augur's scratchpad."

2. **Should SKILL.md be framework?** SKILL.md files define skill procedures. They're authored in the kordinate repo and installed. They should be framework. But they aren't currently registered in KORD.json at all. The migration should register them.

3. **routes.yaml -- knowledge or runtime?** Currently registered as non-curated. Routes define an agent's API surface. They're closer to framework (installed from repo) but are sometimes regenerated. Recommend: `framework: true` for routes.yaml, since they should only change via install.

4. **What about `config.yaml` and `config-acl.yaml`?** These have their own field-level ACL in the guard already. They should be `framework: true` with the existing ACL as an additional layer for field-level control.
