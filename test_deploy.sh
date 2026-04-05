#!/bin/bash
set -euo pipefail
# Test deploy-runtime.sh backend pool generation

TEST_ROOT="/tmp/test_kord"
RUNTIME_ROOT="/tmp/test_kord_runtime"
rm -rf "$TEST_ROOT" "$RUNTIME_ROOT"
mkdir -p "$TEST_ROOT/agents/test-agent/memory"
mkdir -p "$TEST_ROOT/agents/test-agent/skills/test-skill"
mkdir -p "$TEST_ROOT/lib/scripts"

cp /kord/projects/kore/lib/scripts/deploy-runtime.sh "$TEST_ROOT/lib/scripts/deploy-runtime.sh"
chmod +x "$TEST_ROOT/lib/scripts/deploy-runtime.sh"

cat > "$TEST_ROOT/agents/test-agent/IDENTITY.md" << 'IDENTITY'
---
name: test-agent
description: Test agent
profile: openai
model: deepseek-chat
base_url: https://api.deepseek.com
backend_name: deepseek-primary
backend_strategy: hash
api_key_env: DEEPSEEK_API_KEY
color: blue
memory: user
tools:
  - Read
  - Edit
---
# Test Agent
IDENTITY

cat > "$TEST_ROOT/agents/test-agent/BACKENDS.json" << 'BACKENDS'
{
  "selection": "hash",
  "backends": [
    {
      "name": "deepseek-primary",
      "profile": "openai",
      "provider": "openai",
      "model": "deepseek-chat",
      "base_url": "https://api.deepseek.com",
      "api_key_env": "DEEPSEEK_API_KEY"
    },
    {
      "name": "fireworks-fallback",
      "profile": "openai",
      "provider": "openai",
      "model": "accounts/fireworks/models/deepseek-v3p2",
      "base_url": "https://api.fireworks.ai/inference/v1",
      "api_key_env": "FIREWORKS_API_KEY"
    }
  ]
}
BACKENDS

cat > "$TEST_ROOT/agents/test-agent/skills/test-skill/SKILL.md" << 'SKILL'
---
description: Test skill
---
# Test Skill
SKILL

export KORDINATE_HOME="$TEST_ROOT"
export KORD_RUNTIME="$RUNTIME_ROOT"
"$TEST_ROOT/lib/scripts/deploy-runtime.sh" test-agent

echo "\nGenerated runtime files:"
ls -la "$RUNTIME_ROOT/agents/test-agent/"

echo "\n.openclaude-profile.json:"
cat "$RUNTIME_ROOT/agents/test-agent/.openclaude-profile.json"

echo "\n.openclaude-backends.json:"
cat "$RUNTIME_ROOT/agents/test-agent/.openclaude-backends.json"

echo "\nLegacy compatibility files:"
printf ".provider: "; cat "$RUNTIME_ROOT/agents/test-agent/.provider"
printf ".model: "; cat "$RUNTIME_ROOT/agents/test-agent/.model"
printf ".model-spec: "; cat "$RUNTIME_ROOT/agents/test-agent/.model-spec"

echo "\n✅ Deploy runtime test completed successfully"
