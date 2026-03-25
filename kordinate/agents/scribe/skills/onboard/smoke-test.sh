#!/bin/bash
# smoke-test.sh — Runtime verification for kordinate + Claude Code integration
#
# Level 3 resource for the onboard skill. Referenced by claude-checklist.md.
#
# Runs structural checks (fast, free) and optionally runtime checks (uses API).
# Usage:
#   ./smoke-test.sh              # structural checks only
#   ./smoke-test.sh --runtime    # structural + runtime checks (uses claude --print)

set -euo pipefail

KORDINATE_HOME="${KORDINATE_HOME:-$HOME/.kord}"
CLAUDE_HOME="$HOME/.claude"
PASS=0
FAIL=0
SKIP=0

pass() { echo "  ✓ $1"; PASS=$((PASS + 1)); }
fail() { echo "  ✗ $1"; FAIL=$((FAIL + 1)); }
skip() { echo "  - $1 (skipped)"; SKIP=$((SKIP + 1)); }

section() { echo; echo "── $1 ──"; }

# ─── Structural Checks ───

section "Kordinate Source ($KORDINATE_HOME)"

# Agents have IDENTITY.md with required fields
for agent_dir in "$KORDINATE_HOME"/agents/*/; do
  name=$(basename "$agent_dir")
  id_file="$agent_dir/IDENTITY.md"
  if [ -f "$id_file" ]; then
    # Check kordinate properties
    if grep -q '^curated:' "$id_file" && grep -q '^scope:' "$id_file"; then
      pass "$name/IDENTITY.md — has kordinate properties"
    else
      fail "$name/IDENTITY.md — missing curated or scope"
    fi
    # Check Claude fields
    if grep -q '^name:' "$id_file" && grep -q '^description:' "$id_file" && grep -q '^tools:' "$id_file"; then
      pass "$name/IDENTITY.md — has Claude fields"
    else
      fail "$name/IDENTITY.md — missing name, description, or tools"
    fi
  else
    fail "$name/IDENTITY.md — not found"
  fi
done

# Shared protocols
for proto in memory-protocol.md auth-protocol.md credentials-protocol.md; do
  if [ -f "$KORDINATE_HOME/shared/$proto" ]; then
    pass "shared/$proto exists"
  else
    fail "shared/$proto missing"
  fi
done

# KORD.json valid
kord_json="$KORDINATE_HOME/KORD.json"
if [ -f "$kord_json" ] && jq empty "$kord_json" 2>/dev/null; then
  count=$(jq length "$kord_json")
  pass "KORD.json valid ($count entries)"
else
  fail "KORD.json missing or invalid"
fi

# Kord contracts
section "Kord Contracts"
for kord_dir in "$KORDINATE_HOME"/kords/*/; do
  kord_name=$(basename "$kord_dir")
  contract="$kord_dir/contract.md"
  if [ -f "$contract" ]; then
    provider=$(grep '^provider:' "$contract" | head -1 | sed 's/provider: *//')
    mode=$(grep '^mode:' "$contract" | head -1 | sed 's/mode: *//')
    if [ -n "$provider" ] && [ -n "$mode" ]; then
      pass "$kord_name — provider=$provider, mode=$mode"
    else
      fail "$kord_name — missing provider or mode in frontmatter"
    fi
  else
    fail "$kord_name — no contract.md"
  fi
done

# Expiry scripts are executable and return 0 or 1
for expiry in "$KORDINATE_HOME"/kords/*/expiry.sh; do
  [ -f "$expiry" ] || continue
  kord_name=$(basename "$(dirname "$expiry")")
  if bash "$expiry" 2>/dev/null; then
    pass "$kord_name/expiry.sh — returns fresh (0)"
  else
    pass "$kord_name/expiry.sh — returns stale (1)"
  fi
done

section "Claude Native ($CLAUDE_HOME)"

# Agent files
for agent_dir in "$KORDINATE_HOME"/agents/*/; do
  name=$(basename "$agent_dir")
  agent_file="$CLAUDE_HOME/agents/$name.md"
  if [ -f "$agent_file" ]; then
    # Should NOT have kordinate properties
    if grep -q '^curated:' "$agent_file" || grep -q '^preloaded:' "$agent_file" || grep -q '^scope:' "$agent_file"; then
      fail "agents/$name.md — still has kordinate properties (should be stripped)"
    else
      pass "agents/$name.md — clean (no kordinate properties)"
    fi
  else
    fail "agents/$name.md — not found"
  fi
done

# Agent memory indexes
for agent_dir in "$KORDINATE_HOME"/agents/*/; do
  name=$(basename "$agent_dir")
  mem_file="$CLAUDE_HOME/agent-memory/$name/MEMORY.md"
  if [ -f "$mem_file" ]; then
    lines=$(wc -l < "$mem_file")
    if [ "$lines" -le 200 ]; then
      # Check that links point to existing files
      broken=0
      while IFS= read -r line; do
        # Extract path from markdown links: [name](path)
        path=$(echo "$line" | grep -oP '\]\(\K[^)]+' 2>/dev/null || true)
        [ -z "$path" ] && continue
        [ -f "$path" ] || ((broken++))
      done < "$mem_file"
      if [ "$broken" -eq 0 ]; then
        pass "agent-memory/$name/MEMORY.md — index OK ($lines lines, no broken links)"
      else
        fail "agent-memory/$name/MEMORY.md — $broken broken links"
      fi
    else
      fail "agent-memory/$name/MEMORY.md — over 200 lines ($lines)"
    fi
  else
    fail "agent-memory/$name/MEMORY.md — not found"
  fi
done

# CLAUDE.md
section "CLAUDE.md & Shared"
if [ -f "$CLAUDE_HOME/CLAUDE.md" ]; then
  if grep -q '/boot' "$CLAUDE_HOME/CLAUDE.md"; then
    pass "CLAUDE.md contains /boot instruction"
  else
    fail "CLAUDE.md missing /boot instruction"
  fi
  for proto in memory-protocol auth-protocol credentials-protocol; do
    if grep -q "$proto" "$CLAUDE_HOME/CLAUDE.md"; then
      pass "CLAUDE.md @imports $proto"
    else
      fail "CLAUDE.md missing @import for $proto"
    fi
  done
else
  fail "CLAUDE.md not found"
fi

# Global skills
section "Skills"
for skill in boot kord authenticate merge; do
  if [ -f "$CLAUDE_HOME/skills/$skill/SKILL.md" ]; then
    pass "skills/$skill/ — present"
  else
    fail "skills/$skill/ — missing"
  fi
done

# Agent skills
for agent_dir in "$KORDINATE_HOME"/agents/*/; do
  name=$(basename "$agent_dir")
  [ -d "$agent_dir/skills" ] || continue
  for skill_dir in "$agent_dir"/skills/*/; do
    skill_name=$(basename "$skill_dir")
    if [ -f "$CLAUDE_HOME/skills/$skill_name/SKILL.md" ]; then
      pass "skills/$skill_name/ — synced from $name"
    else
      fail "skills/$skill_name/ — not synced (expected from $name)"
    fi
  done
done

# Guard
section "Guard"
settings="$CLAUDE_HOME/settings.json"
if [ -f "$settings" ]; then
  if jq -e '.hooks.PreToolUse' "$settings" >/dev/null 2>&1; then
    if jq -r '.hooks.PreToolUse[].hooks[].command' "$settings" 2>/dev/null | grep -q 'guard.sh'; then
      pass "Guard hook registered (PreToolUse → guard.sh)"
    else
      fail "Guard hook present but doesn't point to guard.sh"
    fi
  else
    fail "No PreToolUse hook in settings.json"
  fi
else
  fail "settings.json not found"
fi

# Test guard behavior
guard_sh="$KORDINATE_HOME/agents/scribe/skills/remember/guard.sh"
if [ -f "$guard_sh" ]; then
  # Should block curated kordinate file without auth
  rm -f /tmp/.scribe-auth
  result=$(echo '{"tool_input":{"file_path":"'"$HOME"'/.kord/agents/scribe/IDENTITY.md"}}' | bash "$guard_sh" 2>/dev/null; echo $?)
  if [ "$(echo "$result" | tail -1)" = "2" ]; then
    pass "Guard blocks curated file without auth"
  else
    fail "Guard should block curated file without auth (got exit $result)"
  fi

  # Should allow with auth
  touch /tmp/.scribe-auth
  result=$(echo '{"tool_input":{"file_path":"'"$HOME"'/.kord/agents/scribe/IDENTITY.md"}}' | bash "$guard_sh" 2>/dev/null; echo $?)
  rm -f /tmp/.scribe-auth
  if [ "$(echo "$result" | tail -1)" = "0" ]; then
    pass "Guard allows curated file with scribe auth"
  else
    fail "Guard should allow with auth (got exit $result)"
  fi

  # Should allow non-kord paths
  result=$(echo '{"tool_input":{"file_path":"/tmp/test.md"}}' | bash "$guard_sh" 2>/dev/null; echo $?)
  if [ "$(echo "$result" | tail -1)" = "0" ]; then
    pass "Guard allows non-kord paths"
  else
    fail "Guard should allow non-kord paths (got exit $result)"
  fi
else
  fail "guard.sh not found"
fi

# ─── Runtime Checks (optional) ───

if [ "${1:-}" = "--runtime" ]; then
  section "Runtime Checks (claude --print)"

  if ! command -v claude &>/dev/null; then
    fail "claude command not found — skipping runtime checks"
  else
    RUNTIME_PASS=0
    RUNTIME_FAIL=0

    runtime_test() {
      local name="$1" agent_flag="$2" prompt="$3" expect="$4"
      local output
      if [ -n "$agent_flag" ]; then
        output=$(claude --print --agent "$agent_flag" --dangerously-skip-permissions "$prompt" 2>/dev/null) || true
      else
        output=$(claude --print --dangerously-skip-permissions "$prompt" 2>/dev/null) || true
      fi
      if echo "$output" | grep -qi "$expect"; then
        pass "$name"
        RUNTIME_PASS=$((RUNTIME_PASS + 1))
      else
        fail "$name (expected '$expect' in output)"
        RUNTIME_FAIL=$((RUNTIME_FAIL + 1))
      fi
    }

    # Subagent spawning
    for agent in deployer scribe sauron designer; do
      runtime_test \
        "Spawn $agent" \
        "$agent" \
        "Respond with exactly one word: your agent name from your identity." \
        "$agent"
    done

    # Boot loads memory
    runtime_test \
      "Boot loads protocols" \
      "scribe" \
      "Read all files in $KORDINATE_HOME/shared/ and list the filenames you found. Nothing else." \
      "memory-protocol"

    # Agent reads own memory
    runtime_test \
      "Deployer reads memory" \
      "deployer" \
      "List the filenames in $KORDINATE_HOME/agents/deployer/memory/. Just filenames, one per line." \
      "infra.md"

    # Cache invalidation — expiry check
    test_kord="deployer-default"
    test_kord_dir="$KORDINATE_HOME/kords/$test_kord"
    if [ -d "$test_kord_dir" ]; then
      # Ensure stale state
      rm -f "$test_kord_dir/.valid"
      if ! bash "$test_kord_dir/expiry.sh" 2>/dev/null; then
        pass "Cache invalidation — stale without .valid"
      else
        fail "Cache invalidation — should be stale without .valid"
      fi
      # Restore fresh state
      echo "$(date -Iseconds)" > "$test_kord_dir/.valid"
      if [ -f "$test_kord_dir/data.md" ]; then
        if bash "$test_kord_dir/expiry.sh" 2>/dev/null; then
          pass "Cache invalidation — fresh with .valid + data.md"
        else
          fail "Cache invalidation — should be fresh with .valid + data.md"
        fi
      else
        skip "Cache invalidation — no data.md to test fresh state"
      fi
    else
      skip "Cache invalidation — $test_kord not found"
    fi

    echo
    echo "Runtime: $RUNTIME_PASS passed, $RUNTIME_FAIL failed"
  fi
else
  section "Runtime Checks"
  skip "Run with --runtime flag to test (uses claude --print, costs API calls)"
fi

# ─── Summary ───

echo
echo "═══════════════════════════════"
echo "  Passed: $PASS  Failed: $FAIL  Skipped: $SKIP"
if [ "$FAIL" -gt 0 ]; then
  echo "  STATUS: FAILING"
  exit 1
else
  echo "  STATUS: OK"
  exit 0
fi
