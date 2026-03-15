Write or update an agent's CLAUDE.md using the unified template.

**Input**: $ARGUMENTS (required: agent name. Optional: inline overrides for specific sections.)

## Template

Every agent CLAUDE.md MUST follow this structure exactly:

```
---
name: <agent-name>
model: <inherit|sonnet|opus|haiku>
color: <color>
tools:
  - <tool1>
  - <tool2>
triggers:
  - "<trigger phrase 1>"
  - "<trigger phrase 2>"
---

# <Name> — <Role> Agent

<One-line mission statement>

## Context

<What to read/consult before acting — including /consult calls to other agents>

## Tools

| Tool | Type | Purpose |
|------|------|---------|
| <tool> | <repo/script/MCP/PyPI> | <what it does> |

## Workflow

1. **Step** — description
2. **Step** — description

## Rules

Shared:
- Read CLAUDE.md before every operation.
- Never write .md files directly — delegate to scribe.
- Commit with `[<agent-name>]` in the message.
- Project-specific artifacts go in the project repo, not the profile repo.

Agent-specific:
- <rules unique to this agent>

## Memory

On every invocation, run /boot before proceeding with your task.
```

## Steps

1. **Read current state** — read `agents/<name>/CLAUDE.md` if it exists.

2. **Gather agent-specific content**:
   - If updating: preserve existing frontmatter, Context, Tools, Workflow, and agent-specific Rules. Only restructure to match the template.
   - If creating new: ask the caller for: mission, context sources, tools, workflow steps, and agent-specific rules.

3. **Build Tools table** — scan the agent's directory for scripts, check if it references any repos (klog, nokrashi-tools, stoik, orchestrator), check if it uses MCPs (grafana, gemini), check if it uses bin/ scripts.

4. **Apply template** — write the CLAUDE.md following the exact template above. Ensure:
   - Shared rules are IDENTICAL across all agents (copy verbatim)
   - Memory section is IDENTICAL across all agents (copy verbatim)
   - Frontmatter has all required fields
   - Tools table lists every tool the agent uses

5. **Validate** — diff against the template structure. Every section heading must be present in order: Context, Tools, Workflow, Rules, Memory.

6. **Write** — use Edit tool to update the file. Authenticate as scribe first.

## Rules

- NEVER omit the shared rules — they are mandatory for all agents.
- NEVER change the Memory section wording.
- Preserve all agent-specific content when restructuring.
- If the agent has no tools beyond standard Claude Code tools, write "Standard Claude Code tools only (Read, Edit, Write, Bash, Grep, Glob)" in the Tools table.
