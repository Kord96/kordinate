#!/bin/bash
# Test parsing model and profile from IDENTITY.md frontmatter

TEST_FILE="/tmp/test_identity.md"
cat > "$TEST_FILE" << 'CONTENT'
---
name: test-agent
description: Test agent with profile
model: haiku
profile: deepseek-chat
color: blue
memory: user
tools:
  - Read
  - Edit
---
# Test Agent

This is a test agent.
CONTENT

echo "Test file created at $TEST_FILE"
echo ""
echo "Extracting model:"
MODEL=$(sed -n 's/^model: *//p' "$TEST_FILE" | head -1)
echo "Model: '$MODEL'"
echo ""
echo "Extracting profile:"
PROFILE=$(sed -n 's/^profile: *//p' "$TEST_FILE" | head -1)
echo "Profile: '$PROFILE'"
